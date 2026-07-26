from perennia_crud import EntitySchema

# raw_materials is the material *master* row only (name/unit/shelf life/
# default supplier/status). Stock levels live in raw_material_inventory
# and the movement log in inventory_movements - both 1:1/1:many companion
# tables perennia-crud doesn't model, handled directly below as before.
RAW_MATERIAL_SCHEMA = EntitySchema(
    table="raw_materials",
    fields=["name", "unit", "shelf_life_days", "default_supplier_id", "status"],
    primary_key="id",
    soft_delete=False,
)
