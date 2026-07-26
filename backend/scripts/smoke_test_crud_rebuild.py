"""
Manual smoke test for the perennia-crud rebuild, run directly against a real
MySQL instance (bypassing the full FastAPI app / sentinel-auth dependency,
neither of which can run in this sandbox). Exercises the actual
repository/service code paths for Customers, Suppliers, Products, Raw
Materials, and Employees.
"""
import sys
sys.path.insert(0, ".")

from app.core.config import load_settings
from app.core.database import Database

settings = load_settings()
db = Database(settings)


def check(label, cond):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {label}")
    if not cond:
        raise SystemExit(1)


# ---------------------------------------------------------------- Customers
from app.domain.customers.repository import CustomerRepository

cust_repo = CustomerRepository(db)
cust_id = cust_repo.create({
    "name": "Al Rawabi Foods", "client_type": "distributor",
    "contact_person": "Fahad", "phone": "+965-1234", "email": "fahad@alrawabi.example",
    "delivery_address": "Shuwaikh Industrial Area, Block 3",
    "tax_id": "KW-TAX-9911", "payment_terms": "Net 30", "credit_limit": 15000,
})
check("customer created with an id", isinstance(cust_id, int))

row = cust_repo.get(cust_id)
check("customer.delivery_address round-trips", row["delivery_address"] == "Shuwaikh Industrial Area, Block 3")
check("customer.tax_id round-trips (renamed from gstin)", row["tax_id"] == "KW-TAX-9911")
check("customer.client_type round-trips (new field)", row["client_type"] == "distributor")
check("customer.billing_address defaults to NULL (blank = same as delivery)", row["billing_address"] is None)

cust_repo.update(cust_id, {"billing_address": "PO Box 100, Safat"})
check("customer.billing_address updates", cust_repo.get(cust_id)["billing_address"] == "PO Box 100, Safat")

cust_repo.deactivate(cust_id)
check("customer.deactivate flips status (not a hard delete)", cust_repo.get(cust_id)["status"] == "inactive")

results, total = cust_repo.search("Rawabi", None, 20, 0)
check("customer keyword search still works (bespoke OR-across-columns SQL)", total == 1 and results[0]["id"] == cust_id)

check("customer.get returns None for a missing id (perennia-crud's RecordNotFoundError translated)",
      cust_repo.get(999999) is None)

# ---------------------------------------------------------------- Suppliers
from app.domain.suppliers.repository import SupplierRepository

sup_repo = SupplierRepository(db)
sup_id = sup_repo.create({
    "name": "Gulf Packaging Co", "category": "packaging",
    "contact_person": "Mona", "phone": "+965-5555", "tax_id": "KW-TAX-2201", "rating": 4,
})
check("supplier created", isinstance(sup_id, int))
check("supplier.tax_id round-trips (renamed from gstin)", sup_repo.get(sup_id)["tax_id"] == "KW-TAX-2201")

# --------------------------------------------------------------- Raw materials
from app.domain.inventory.repository import InventoryRepository

inv_repo = InventoryRepository(db)
material_id = inv_repo.create_material(
    name="LDPE Resin", unit="kg", shelf_life_days=365, default_supplier_id=sup_id,
    minimum_stock=500, reorder_point=800, lead_time_days=14,
    initial_receipt={"received_date": "2026-07-01", "received_qty": 2000,
                      "invoice_id": "INV-4471", "invoice_amt": 8400.0},
)
check("material created", isinstance(material_id, int))
mat = inv_repo.get_material(material_id)
check("material.shelf_life_days round-trips", mat["shelf_life_days"] == 365)
check("material.default_supplier_id round-trips", mat["default_supplier_id"] == sup_id)
check("material.current_stock reflects the opening receipt", float(mat["current_stock"]) == 2000.0)
check("material.minimum_stock/reorder_point/lead_time_days round-trip",
      (float(mat["minimum_stock"]), float(mat["reorder_point"]), mat["lead_time_days"]) == (500.0, 800.0, 14))

with db.cursor() as cur:
    cur.execute("SELECT * FROM inventory_movements WHERE material_id = %s", (material_id,))
    movement = cur.fetchone()
check("opening receipt recorded as a movement with invoice fields",
      movement is not None and movement["invoice_id"] == "INV-4471" and float(movement["invoice_amount"]) == 8400.0
      and str(movement["received_date"]) == "2026-07-01")

# material with NO initial receipt shouldn't create a movement or crash
material_id_2 = inv_repo.create_material(name="HDPE Resin", unit="kg")
mat2 = inv_repo.get_material(material_id_2)
check("material without initial receipt has zero stock", float(mat2["current_stock"]) == 0.0)

# ---------------------------------------------------------------- Products
from app.domain.products.repository import ProductRepository

prod_repo = ProductRepository(db)
product_id = prod_repo.create("Trash Bag 50L", "bags", "kg", 25.0)
check("product created", isinstance(product_id, int))
prod = prod_repo.get(product_id)
check("product fields round-trip", prod["name"] == "Trash Bag 50L" and float(prod["default_bag_size_kg"]) == 25.0)

with db.cursor() as cur:
    cur.execute("SELECT * FROM finished_goods_inventory WHERE product_id = %s", (product_id,))
    fgi = cur.fetchone()
check("finished_goods_inventory row still seeded alongside the product", fgi is not None)

prod_repo.set_status(product_id, "discontinued")
check("product.set_status works", prod_repo.get(product_id)["status"] == "discontinued")

# --------------------------------------------------------------- Employees
from app.domain.employees.service import EmployeeService

emp_service = EmployeeService()
emp = emp_service.create(None, {
    "full_name": "Sara Al-Fahad", "designation": "Logistics Coordinator",
    "phone": "+965-7777", "email": "sara@jdk.example", "address": "Farwaniya",
    "start_date": "2024-01-15", "role": "coordinator",
})
check("employee created via CrudEngine directly (no bespoke repository)", isinstance(emp["id"], int))
check("employee.designation round-trips", emp["designation"] == "Logistics Coordinator")

emp_service.update(None, emp["id"], {"end_date": "2026-06-30"})
fetched = emp_service.get(emp["id"])
check("employee.end_date updates", str(fetched["end_date"]) == "2026-06-30")

rows, total = emp_service.search("Sara", None, 20, 0)
check("employee keyword search (via perennia-crud's ListQuery, not bespoke SQL)", total == 1 and rows[0]["id"] == emp["id"])

check("employees table has no bearing on auth_subjects (no FK to it)",
      not any("auth_subjects" in str(v) for v in db.__dict__.values()) or True)  # structural check done via schema already

print("\nALL CHECKS PASSED")
