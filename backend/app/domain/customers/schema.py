from perennia_crud import EntitySchema

# customers has no deleted_at column - deactivation is a plain status flip
# (status='inactive'), not perennia-crud's soft-delete/restore mechanism.
CUSTOMER_SCHEMA = EntitySchema(
    table="customers",
    fields=[
        "name", "client_type", "contact_person", "email", "phone",
        "delivery_address", "billing_address", "tax_id", "payment_terms",
        "credit_limit", "status", "notes", "created_at", "updated_at",
    ],
    primary_key="id",
    soft_delete=False,
)
