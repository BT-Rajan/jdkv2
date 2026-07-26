from perennia_crud import EntitySchema

# suppliers has no deleted_at column - deactivation is a plain status flip,
# not perennia-crud's soft-delete/restore mechanism.
SUPPLIER_SCHEMA = EntitySchema(
    table="suppliers",
    fields=[
        "name", "contact_person", "phone", "email", "address", "tax_id",
        "category", "rating", "status", "notes", "created_at",
    ],
    primary_key="id",
    soft_delete=False,
)
