from perennia_crud import EntitySchema

# Plain HR directory - deliberately independent of perennia-auth's
# auth_subjects/auth_identifiers and of JDK's own login-linked
# user_profiles/user_admin_audit (see app/domain/users/). `role` here is a
# free-text job title/role label, not an RBAC permission role.
EMPLOYEE_SCHEMA = EntitySchema(
    table="employees",
    fields=[
        "full_name", "designation", "phone", "email", "address",
        "start_date", "end_date", "role", "created_at", "updated_at",
    ],
    primary_key="id",
    soft_delete=False,
)
