"""AI Factory Assistant.

A conversational layer over the same domain repositories used elsewhere in
the app (open orders, finished-goods stock, raw-material stock, MRP
shortages, customers). It answers plain-language questions and, for a
narrow set of stock-update requests, proposes a mutation that is applied
only if the caller holds INVENTORY_ADJUST.

Requires DEEPSEEK_API_KEY to be set; degrades to a "not configured" reply
otherwise rather than failing.
"""
import json

import requests

from app.core.errors import AppError
from app.core.sentinel_access import AuthenticatedIdentity, SentinelAccess
from app.domain.customers.repository import CustomerRepository
from app.domain.inventory.repository import InventoryRepository
from app.domain.orders.repository import OrderRepository
from app.domain.products.repository import ProductRepository
from app.intelligence.mrp_engine import MrpEngine
from app.permissions.definitions import INVENTORY_ADJUST

MAX_LIST = 40


def _fuzzy_match_one(name: str, candidates: list) -> str | None:
    """Resolves a casually-typed name against a known list of exact names:
    exact match first, then an unambiguous substring match. Returns None
    rather than guessing, since this gates real inventory mutations."""
    if not name:
        return None
    name_l = name.strip().lower()
    for c in candidates:
        if c.lower() == name_l:
            return c
    hits = [c for c in candidates if name_l in c.lower() or c.lower() in name_l]
    return hits[0] if len(hits) == 1 else None


class ChatAssistant:
    def __init__(self, order_repo: OrderRepository, product_repo: ProductRepository,
                 inventory_repo: InventoryRepository, customer_repo: CustomerRepository,
                 mrp_engine: MrpEngine, access: SentinelAccess,
                 api_key: str, base_url: str, model: str):
        self._orders = order_repo
        self._products = product_repo
        self._inventory = inventory_repo
        self._customers = customer_repo
        self._mrp = mrp_engine
        self._access = access
        self._api_key = api_key
        self._base_url = base_url
        self._model = model

    def reply(self, message: str, history: list, identity: AuthenticatedIdentity) -> dict:
        if not self._api_key:
            return {
                "reply": "The AI assistant isn't configured yet. Ask an administrator to set DEEPSEEK_API_KEY.",
                "action": None,
            }

        context = self._build_context()
        roles = self._access.get_identity_roles(identity)
        system_prompt = self._system_prompt(context, roles)

        messages = [
            {"role": "user" if m.get("role") == "user" else "assistant", "content": m.get("content", "")}
            for m in history[-10:]
        ]
        messages.append({"role": "user", "content": message})

        try:
            response = requests.post(
                f"{self._base_url}/v1/chat/completions",
                json={
                    "model": self._model,
                    "messages": [{"role": "system", "content": system_prompt}] + messages,
                    "max_tokens": 600,
                    "temperature": 0.7,
                },
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=30,
            )
            response.raise_for_status()
            raw = response.json()["choices"][0]["message"]["content"]
        except Exception:
            raise AppError("chat_upstream_error")

        reply_text, action = self._extract_action(raw)
        reply_text, action = self._apply_action(reply_text, action, identity, context)
        return {"reply": reply_text, "action": action}

    # ---------------------------------------------------------------- context

    def _build_context(self) -> dict:
        products, _ = self._products.search(None, "active", 1000, 0)
        finished_goods = {}
        for p in products:
            fg = self._products.get_finished_goods(p["id"]) or {"available_kg": 0, "available_bags": 0}
            finished_goods[p["name"]] = {
                "product_id": p["id"],
                "bag_size_kg": float(p["default_bag_size_kg"]),
                "available_kg": float(fg["available_kg"] or 0),
                "available_bags": int(fg["available_bags"] or 0),
            }

        materials, _ = self._inventory.search_materials(None, False, 1000, 0)
        material_by_name = {m["name"]: m for m in materials}

        mrp_snapshot = self._mrp.calculate()
        shortages = [m for m in mrp_snapshot["material_requirements"] if m["shortage"]]

        orders, _ = self._orders.search(None, None, None, 1000, 0)
        open_orders = [o for o in orders if o["status"] in OrderRepository.OPEN_STATUSES]

        customers, _ = self._customers.search(None, None, 1000, 0)

        return {
            "finished_goods": finished_goods,
            "materials": material_by_name,
            "shortages": shortages,
            "open_orders": open_orders,
            "customers": customers,
        }

    def _system_prompt(self, ctx: dict, roles: list) -> str:
        fg_lines = "\n".join(
            f"  - {name}: {v['available_kg']:,.0f} kg, {v['available_bags']:,.0f} bags"
            for name, v in ctx["finished_goods"].items()
        ) or "  (none)"

        mat_lines = "\n".join(
            f"  - {m['name']}: {float(m['current_stock']):,.0f} {m['unit']} in stock "
            f"(minimum {float(m['minimum_stock'] or 0):,.0f}, reorder point {float(m['reorder_point'] or 0):,.0f}) "
            f"- status: {m['status']}"
            for m in ctx["materials"].values()
        ) or "  (none)"

        shortage_lines = "\n".join(
            f"  - {s['material_name']}: short {s['net_required']:,.0f} {s['unit']} against current open-order demand"
            for s in ctx["shortages"]
        ) or "  (no material shortages against open orders)"

        open_orders = ctx["open_orders"]
        order_lines = "\n".join(
            f"  - {o['order_no']}: {o['customer_name']} - {o['product_name']}, {float(o['quantity_kg']):,.0f} kg, "
            f"due {o['delivery_date'] or 'no date'}, status: {o['status']}"
            for o in open_orders[:MAX_LIST]
        ) or "  (no open orders)"
        if len(open_orders) > MAX_LIST:
            order_lines += f"\n  ...and {len(open_orders) - MAX_LIST} more open orders not shown here."

        customers = ctx["customers"]
        customer_lines = "\n".join(f"  - {c['name']}" for c in customers[:MAX_LIST]) or "  (none)"
        if len(customers) > MAX_LIST:
            customer_lines += f"\n  ...and {len(customers) - MAX_LIST} more customers not shown here."

        return f"""You are the JDK Factory AI assistant for a manufacturing ERP.
The person asking is a factory user, not a technical person - they know
their materials, products, and orders by casual names. Questions like
"how much cement", "any orders from Acme", or "what's running low" are
real questions you must answer directly using the data below.

Rules:
1. Match casually, not literally - partial names are fine for products,
   materials, customers, and order numbers. List every match, don't ask
   the user to be more specific.
2. Always answer using the exact figures given below. Never tell the user
   to go check a page themselves.
3. Use plain, everyday words.
4. Keep answers short: a sentence or two, lead with the number.
5. If something isn't in the data below, say so plainly in one line.

Finished (bagged/packed) stock right now:
{fg_lines}

Raw material stock:
{mat_lines}

Material shortages against current open-order demand:
{shortage_lines}

Open customer orders - {len(open_orders)} total:
{order_lines}

Customers on file - {len(customers)} total:
{customer_lines}

User role(s): {', '.join(roles) or 'unknown'}

Respond in 1-3 short, plain-language sentences or a short list.

If the user asks to change, update, or set the stock of a FINISHED
PRODUCT, match it to the closest product above and end your reply with
exactly one line:
ACTION: {{"action": "update_finished_goods", "product": "<exact product name from the list above>", "available_kg": <number>, "available_bags": <number>}}
Estimate whichever of kg/bags the user didn't give from the product's
usual bag size. Resolve to the closest match rather than asking a
clarifying question first.

If the user asks to change, update, or set the stock of a RAW MATERIAL,
match it to the closest material above and end your reply with exactly
one line:
ACTION: {{"action": "update_raw_material_stock", "material": "<exact material name from the list above>", "current_stock": <number>}}

Only ever include ONE ACTION line, and only when the user is asking you
to change something or go somewhere - never for plain questions. For any
other request to go do something, end with:
ACTION: {{"action": "navigate", "page": "orders"}}"""

    @staticmethod
    def _extract_action(raw: str):
        if "ACTION:" not in raw:
            return raw.strip(), None
        text_part, action_part = raw.split("ACTION:", 1)
        try:
            action = json.loads(action_part.strip())
        except Exception:
            action = None
        return text_part.strip(), action

    def _apply_action(self, reply_text: str, action: dict | None, identity: AuthenticatedIdentity, ctx: dict):
        if not action:
            return reply_text, None
        act_type = action.get("action")

        if act_type == "update_finished_goods":
            if not self._access.can(identity, INVENTORY_ADJUST):
                return reply_text + "\n\nYour role doesn't have permission to update inventory.", None
            matched = _fuzzy_match_one(str(action.get("product", "")), list(ctx["finished_goods"].keys()))
            if not matched:
                return reply_text + f"\n\nCouldn't match \"{action.get('product', '')}\" to a product - nothing was changed.", None
            try:
                new_kg = float(action["available_kg"])
            except (TypeError, ValueError, KeyError):
                return reply_text + "\n\nCouldn't read the new stock number - nothing was changed.", None

            fg = ctx["finished_goods"][matched]
            delta_kg = new_kg - fg["available_kg"]
            self._products.adjust_finished_goods(fg["product_id"], delta_kg, fg["bag_size_kg"])
            return (
                reply_text + f"\n\nUpdated {matched} stock to {new_kg:,.0f} kg.",
                {"action": "navigate", "page": "products"},
            )

        if act_type == "update_raw_material_stock":
            if not self._access.can(identity, INVENTORY_ADJUST):
                return reply_text + "\n\nYour role doesn't have permission to update raw materials.", None
            mat_names = list(ctx["materials"].keys())
            matched = _fuzzy_match_one(str(action.get("material", "")), mat_names)
            if not matched:
                return reply_text + f"\n\nCouldn't match \"{action.get('material', '')}\" to a raw material - nothing was changed.", None
            try:
                new_stock = float(action["current_stock"])
            except (TypeError, ValueError, KeyError):
                return reply_text + "\n\nCouldn't read the new stock number - nothing was changed.", None

            material = ctx["materials"][matched]
            delta = new_stock - float(material["current_stock"])
            self._inventory.record_movement(material["id"], "adjustment", delta, "ai_chat", identity.subject_id)
            return (
                reply_text + f"\n\nUpdated {matched} stock to {new_stock:,.0f} {material['unit']}.",
                {"action": "navigate", "page": "materials"},
            )

        # navigate or anything unrecognized: pass through, nothing to mutate
        return reply_text, action
