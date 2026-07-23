"""
MRP (Material Requirements Planning) and ATP (Available-to-Promise).

This module contains JDK's own business logic - it is not part of any
perennia package, and doesn't need to be: MRP/ATP is JDK's core value, not
an identity/access/search/notify/files concern. It reads from the domain
repositories (orders, products/formulas, materials/inventory, suppliers)
that already exist.

Calculation chain (docs/features/mrp-and-atp.md):

    Customer Requirement (open orders, grouped by product)
        - Existing Finished Goods
        = Production Requirement
        x Formula (active, versioned)
        = Gross Material Requirement
        - Available Material (current stock)
        = Net Material Requirement ("shortage" when > 0)

Known limitation: JDK does not yet track open purchase orders / expected
supplier receipts as a distinct entity, so "expected supply" below is a
projection (cheapest active supplier's price and lead time) rather than a
commitment already placed. This should be replaced with real PO data once
a Purchasing module exists; every value that is a projection rather than a
committed fact is labelled `is_projected` in the output so the frontend
doesn't present it as certain.
"""
from dataclasses import dataclass, field
from datetime import date, timedelta

from app.domain.orders.repository import OrderRepository
from app.domain.products.repository import ProductRepository
from app.domain.inventory.repository import InventoryRepository
from app.domain.suppliers.repository import SupplierRepository


class MrpEngine:
    def __init__(self, order_repo: OrderRepository, product_repo: ProductRepository,
                 inventory_repo: InventoryRepository, supplier_repo: SupplierRepository):
        self._orders = order_repo
        self._products = product_repo
        self._inventory = inventory_repo
        self._suppliers = supplier_repo

    # ------------------------------------------------------------------ MRP

    def calculate(self) -> dict:
        open_by_product = self._orders.open_orders_by_product()

        production_requirements = []
        gross_material_requirement: dict[int, float] = {}
        material_to_products: dict[int, set[int]] = {}

        for product_id, orders in open_by_product.items():
            product = self._products.get(product_id)
            if not product:
                continue
            finished_goods = self._products.get_finished_goods(product_id) or {"available_kg": 0}
            total_ordered_kg = sum(float(o["quantity_kg"]) for o in orders)
            available_kg = float(finished_goods["available_kg"])
            production_required_kg = max(0.0, total_ordered_kg - available_kg)

            formula = self._products.get_active_formula(product_id)
            production_requirements.append({
                "product_id": product_id,
                "product_name": product["name"],
                "total_ordered_kg": total_ordered_kg,
                "finished_goods_kg": available_kg,
                "production_required_kg": production_required_kg,
                "has_active_formula": formula is not None,
                "contributing_orders": [
                    {"order_id": o["id"], "order_no": o["order_no"], "customer_name": o["customer_name"],
                     "quantity_kg": float(o["quantity_kg"]), "delivery_date": o["delivery_date"]}
                    for o in orders
                ],
            })

            if formula and production_required_kg > 0:
                for line in formula["lines"]:
                    material_id = line["material_id"]
                    required = production_required_kg * float(line["quantity_per_unit"])
                    gross_material_requirement[material_id] = gross_material_requirement.get(material_id, 0.0) + required
                    material_to_products.setdefault(material_id, set()).add(product_id)

        material_requirements = []
        for material_id, gross in gross_material_requirement.items():
            material = self._inventory.get_material(material_id)
            if not material:
                continue
            current_stock = float(material["current_stock"])
            net_required = max(0.0, gross - current_stock)
            shortage = net_required > 0

            suggested_supplier = None
            estimated_supply_date = None
            if shortage:
                candidates = self._suppliers.suppliers_for_material(material_id)
                if candidates:
                    best = candidates[0]  # cheapest active, per SupplierRepository.suppliers_for_material
                    suggested_supplier = {
                        "supplier_id": best["supplier_id"],
                        "supplier_name": best["supplier_name"],
                        "price": float(best["price"]),
                        "lead_time_days": best["lead_time_days"],
                        "minimum_order_qty": float(best["minimum_order_qty"]),
                        "is_projected": True,
                    }
                    estimated_supply_date = date.today() + timedelta(days=best["lead_time_days"])

            material_requirements.append({
                "material_id": material_id,
                "material_name": material["name"],
                "unit": material["unit"],
                "gross_required": gross,
                "current_stock": current_stock,
                "net_required": net_required,
                "shortage": shortage,
                "affected_product_ids": sorted(material_to_products.get(material_id, [])),
                "suggested_supplier": suggested_supplier,
                "estimated_supply_date": estimated_supply_date,
            })

        material_requirements.sort(key=lambda m: (not m["shortage"], -m["net_required"]))

        return {
            "production_requirements": production_requirements,
            "material_requirements": material_requirements,
            "has_shortages": any(m["shortage"] for m in material_requirements),
        }

    def why_is_material_required(self, material_id: int) -> dict:
        """Traceability: material shortage -> requirement -> product -> orders."""
        snapshot = self.calculate()
        entry = next((m for m in snapshot["material_requirements"] if m["material_id"] == material_id), None)
        if entry is None:
            return {"material_id": material_id, "affected_products": []}

        affected = []
        for product_id in entry["affected_product_ids"]:
            prod_entry = next(
                (p for p in snapshot["production_requirements"] if p["product_id"] == product_id), None
            )
            if prod_entry:
                affected.append(prod_entry)
        return {**entry, "affected_products": affected}

    # ------------------------------------------------------------------ ATP

    def available_to_promise(self, product_id: int, requested_kg: float) -> dict:
        product = self._products.get(product_id)
        if not product:
            raise ValueError(f"product {product_id} not found")

        finished_goods = self._products.get_finished_goods(product_id) or {"available_kg": 0}
        available_now = float(finished_goods["available_kg"])
        # Existing commitments already competing for the same finished goods:
        open_orders = self._orders.open_orders_by_product().get(product_id, [])
        already_committed_kg = sum(float(o["quantity_kg"]) for o in open_orders)
        uncommitted_finished_goods = max(0.0, available_now - already_committed_kg)

        promptly_available_kg = min(requested_kg, uncommitted_finished_goods)
        remaining_kg = max(0.0, requested_kg - promptly_available_kg)

        constraints = []
        estimated_date = date.today()

        if remaining_kg > 0:
            formula = self._products.get_active_formula(product_id)
            if not formula:
                constraints.append({"reason": "no_active_formula", "detail": "Product has no active formula to plan production."})
            else:
                max_lead_days = 0
                for line in formula["lines"]:
                    material = self._inventory.get_material(line["material_id"])
                    if not material:
                        continue
                    required_for_remaining = remaining_kg * float(line["quantity_per_unit"])
                    current_stock = float(material["current_stock"])
                    if required_for_remaining > current_stock:
                        shortage = required_for_remaining - current_stock
                        candidates = self._suppliers.suppliers_for_material(line["material_id"])
                        lead_days = candidates[0]["lead_time_days"] if candidates else None
                        constraints.append({
                            "material_id": line["material_id"],
                            "material_name": material["name"],
                            "shortage": shortage,
                            "unit": material["unit"],
                            "supplier_lead_time_days": lead_days,
                            "is_projected": True,
                        })
                        if lead_days:
                            max_lead_days = max(max_lead_days, lead_days)
                estimated_date = date.today() + timedelta(days=max_lead_days)

        return {
            "product_id": product_id,
            "requested_kg": requested_kg,
            "promptly_available_kg": promptly_available_kg,
            "remaining_kg": remaining_kg,
            "can_fully_promise_now": remaining_kg == 0,
            "constraints": constraints,
            "estimated_fulfillment_date": estimated_date if remaining_kg > 0 else date.today(),
        }
