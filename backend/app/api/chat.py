from fastapi import APIRouter, Depends

from app.core.sentinel_access import AuthenticatedIdentity

from app.core.security import require_permission, access
from app.core.database import Database
from app.core.config import load_settings
from app.domain.orders.repository import OrderRepository
from app.domain.products.repository import ProductRepository
from app.domain.inventory.repository import InventoryRepository
from app.domain.customers.repository import CustomerRepository
from app.domain.suppliers.repository import SupplierRepository
from app.intelligence.mrp_engine import MrpEngine
from app.intelligence.chat_assistant import ChatAssistant
from app.permissions.definitions import CHAT_USE
from app.models.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["chat"])

_settings = load_settings()
_db = Database(_settings)
_order_repo = OrderRepository(_db)
_product_repo = ProductRepository(_db)
_inventory_repo = InventoryRepository(_db)
_customer_repo = CustomerRepository(_db)
_mrp_engine = MrpEngine(_order_repo, _product_repo, _inventory_repo, SupplierRepository(_db))
_assistant = ChatAssistant(
    _order_repo, _product_repo, _inventory_repo, _customer_repo, _mrp_engine, access,
    api_key=_settings.deepseek_api_key,
    base_url=_settings.deepseek_base_url,
    model=_settings.deepseek_model,
)


@router.post("/chat", response_model=ChatResponse)
def ai_chat(body: ChatRequest, identity: AuthenticatedIdentity = Depends(require_permission(CHAT_USE))):
    result = _assistant.reply(body.message, [m.model_dump() for m in body.history], identity)
    return ChatResponse(**result)
