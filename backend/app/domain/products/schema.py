from perennia_crud import EntitySchema

# products has no deleted_at column - discontinuing a product is a plain
# status flip, not perennia-crud's soft-delete/restore mechanism.
PRODUCT_SCHEMA = EntitySchema(
    table="products",
    fields=[
        "name", "category", "unit_of_measure", "default_bag_size_kg",
        "status", "created_at",
    ],
    primary_key="id",
    soft_delete=False,
)
