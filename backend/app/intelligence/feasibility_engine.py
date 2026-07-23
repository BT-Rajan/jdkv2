"""
Feasibility and risk assessment (docs/features/feasibility-and-risk.md).

Built directly on MrpEngine.available_to_promise() - feasibility is "can we
meet this order's required date", which is ATP's promptly-available/
remaining split plus a comparison against the order's delivery_date. This
module adds no new data source; it interprets ATP's output against a date.

Outcome classification (five per the spec):
    feasible              - fully promptable now, or achievable by the
                             required date even if not from current stock
    partially_feasible    - some quantity available now, remainder would
                             land after the required date
    feasible_on_later_date - nothing available now, but a concrete achievable
                             date exists after the required date
    at_risk               - order has no required date to assess against, or
                             a date could be estimated but sits close enough
                             to today that a small slip would miss it
    not_feasible           - a shortage exists and no supplier/lead-time data
                             is available to estimate a date at all

This is a judgment call about outcome boundaries where the spec deliberately
leaves "the exact calculation" open; the constraints list underneath always
shows the concrete facts (available_kg, shortages, supplier lead times) so a
human can override the label.
"""
from dataclasses import dataclass
from datetime import date

from app.domain.orders.repository import OrderRepository
from app.intelligence.mrp_engine import MrpEngine

FEASIBLE = "feasible"
PARTIALLY_FEASIBLE = "partially_feasible"
FEASIBLE_ON_LATER_DATE = "feasible_on_later_date"
AT_RISK = "at_risk"
NOT_FEASIBLE = "not_feasible"


class FeasibilityEngine:
    def __init__(self, order_repo: OrderRepository, mrp_engine: MrpEngine):
        self._orders = order_repo
        self._mrp = mrp_engine

    def assess_order(self, order_id: int) -> dict:
        order = self._orders.get(order_id)
        if not order:
            raise ValueError(f"order {order_id} not found")

        atp = self._mrp.available_to_promise(order["product_id"], float(order["quantity_kg"]))
        delivery_date: date | None = order["delivery_date"]

        unresolvable_shortage = atp["remaining_kg"] > 0 and any(
            c.get("shortage") is not None and not c.get("supplier_lead_time_days")
            for c in atp["constraints"]
        )

        if atp["can_fully_promise_now"]:
            outcome = FEASIBLE
        elif unresolvable_shortage:
            outcome = NOT_FEASIBLE
        elif delivery_date is None:
            outcome = AT_RISK
        elif atp["estimated_fulfillment_date"] <= delivery_date:
            outcome = FEASIBLE
        elif atp["promptly_available_kg"] > 0:
            outcome = PARTIALLY_FEASIBLE
        else:
            outcome = FEASIBLE_ON_LATER_DATE

        return {
            "order_id": order_id,
            "order_no": order["order_no"],
            "outcome": outcome,
            "required_date": delivery_date,
            "estimated_fulfillment_date": atp["estimated_fulfillment_date"],
            "promptly_available_kg": atp["promptly_available_kg"],
            "remaining_kg": atp["remaining_kg"],
            "requested_kg": atp["requested_kg"],
            "constraints": atp["constraints"],
        }

    def assess_all_open_orders(self) -> list[dict]:
        results = []
        for order_id in self._orders.list_all_ids():
            order = self._orders.get(order_id)
            if order and order["status"] in OrderRepository.OPEN_STATUSES:
                results.append(self.assess_order(order_id))
        # Highest-risk first so the dashboard leads with what needs attention.
        risk_rank = {NOT_FEASIBLE: 0, AT_RISK: 1, PARTIALLY_FEASIBLE: 2, FEASIBLE_ON_LATER_DATE: 3, FEASIBLE: 4}
        results.sort(key=lambda r: risk_rank.get(r["outcome"], 5))
        return results
