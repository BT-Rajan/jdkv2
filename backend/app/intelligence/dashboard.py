"""
Executive dashboard: a single "what needs attention today" view, composed
from the domain repositories and the MRP/feasibility engines. Deliberately
does not attempt to show every data point (see docs/features/reports-and-dashboard.md) -
it surfaces counts and the highest-risk items, and links out to the detailed
views (orders, MRP, inventory) for the rest.
"""
from app.domain.orders.repository import OrderRepository
from app.domain.inventory.repository import InventoryRepository
from app.intelligence.mrp_engine import MrpEngine
from app.intelligence.feasibility_engine import FeasibilityEngine, FEASIBLE


class DashboardService:
    def __init__(self, order_repo: OrderRepository, inventory_repo: InventoryRepository,
                 mrp_engine: MrpEngine, feasibility_engine: FeasibilityEngine):
        self._orders = order_repo
        self._inventory = inventory_repo
        self._mrp = mrp_engine
        self._feasibility = feasibility_engine

    def summary(self) -> dict:
        open_by_product = self._orders.open_orders_by_product()
        open_order_count = sum(len(v) for v in open_by_product.values())

        materials, _ = self._inventory.search_materials(keyword=None, low_stock_only=True, limit=100, offset=0)

        mrp_snapshot = self._mrp.calculate()
        shortages = [m for m in mrp_snapshot["material_requirements"] if m["shortage"]]

        feasibility_results = self._feasibility.assess_all_open_orders()
        at_risk_orders = [r for r in feasibility_results if r["outcome"] != FEASIBLE]

        return {
            "open_order_count": open_order_count,
            "products_with_open_demand": len(open_by_product),
            "low_stock_material_count": len(materials),
            "low_stock_materials": materials[:10],
            "material_shortage_count": len(shortages),
            "top_material_shortages": shortages[:10],
            "orders_needing_attention_count": len(at_risk_orders),
            "orders_needing_attention": at_risk_orders[:10],
        }
