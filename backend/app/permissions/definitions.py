"""
Central permission vocabulary for JDK.

perennia-access owns roles, permissions, and the authorization decision
itself; this module only owns JDK's *vocabulary* (which permissions exist,
and which roles grant which permissions) and seeds that vocabulary into
perennia-access on startup - see docs/07-security-and-roles.md.

Nothing in this application checks a role name to make an authorization
decision (e.g. `if role == "administrator"`). Every protected route checks
a permission code through perennia-access - see app/core/security.py.

Status: the permission codes for every business capability boundary
(docs/06-architecture.md section 8) are declared up front so the vocabulary
is stable as each module is built. Only the User Administration permissions
are enforced by real endpoints as of this phase; the rest are reserved for
the modules described in the project roadmap (see README.md) and are seeded
here so role definitions don't need to change shape later.
"""
from perennia_access import PerenniaAccess, AuthenticatedIdentity

# A synthetic identity for JDK's own internal operations (e.g. reindexing a
# record after a write) that are not really "a user's action" even though
# they happen inside a request handler. perennia-access has no built-in
# notion of a system/service account, and user_roles.subject_id has no
# foreign key back to perennia-auth's subjects (it is intentionally decoupled -
# see perennia-access's schema.sql) - so this works as a role assignment
# perennia-access will happily authorize, without ever being a real
# perennia-auth account someone could sign in as.
SYSTEM_SUBJECT_ID = "00000000-0000-0000-0000-000000000000"
SYSTEM_IDENTITY = AuthenticatedIdentity(subject_id=SYSTEM_SUBJECT_ID, session_id="system")

# --- User Administration (this phase) ---------------------------------------
USERS_VIEW = "users.view"
USERS_MANAGE = "users.manage"  # create, update, promote/demote, deactivate

# --- Customers ---------------------------------------------------------------
CUSTOMERS_VIEW = "customer.view"
CUSTOMERS_MANAGE = "customer.manage"

# --- Products & Formulas -----------------------------------------------------
PRODUCTS_VIEW = "product.view"
PRODUCTS_MANAGE = "product.manage"  # includes formula versioning - sensitive

# --- Materials & Inventory ----------------------------------------------------
INVENTORY_VIEW = "inventory.view"
INVENTORY_ADJUST = "inventory.adjust"  # sensitive - auditable

# --- Suppliers ----------------------------------------------------------------
SUPPLIERS_VIEW = "supplier.view"
SUPPLIERS_MANAGE = "supplier.manage"

# --- Customer Orders -----------------------------------------------------------
ORDERS_VIEW = "order.view"
ORDERS_CREATE = "order.create"
ORDERS_EDIT = "order.edit"
ORDERS_DELETE = "order.delete"

# --- MRP & ATP / Feasibility & Risk --------------------------------------------
MRP_VIEW = "mrp.view"
MRP_EXECUTE = "mrp.execute"

# --- Daily Status & Reports -----------------------------------------------------
REPORTS_VIEW = "reports.view"

# --- perennia-search integration: codes fixed by perennia-search itself --------
SEARCH_EXECUTE = "search.execute"
SEARCH_MANAGE = "search.manage"

# --- perennia-notify integration: codes fixed by perennia-notify itself --------
NOTIFY_SEND = "notify.send"
NOTIFY_READ = "notify.read"
NOTIFY_MANAGE = "notify.manage"

# --- perennia-files integration: codes fixed by perennia-files itself ----------
FILE_UPLOAD = "file.upload"
FILE_VIEW = "file.view"
FILE_DOWNLOAD = "file.download"
FILE_CREATE_VERSION = "file.create_version"
FILE_DELETE = "file.delete"
FILE_RESTORE = "file.restore"
FILE_PROCESS = "file.process"
FILE_AI = "file.ai"

PERMISSIONS: list[tuple[str, str]] = [
    (USERS_VIEW, "View JDK user accounts"),
    (USERS_MANAGE, "Create, update, promote/demote and deactivate JDK users"),
    (CUSTOMERS_VIEW, "View customer records"),
    (CUSTOMERS_MANAGE, "Create and edit customer records"),
    (PRODUCTS_VIEW, "View products and their formulas"),
    (PRODUCTS_MANAGE, "Create and version product formulas"),
    (INVENTORY_VIEW, "View raw material and finished goods inventory"),
    (INVENTORY_ADJUST, "Adjust inventory stock levels"),
    (SUPPLIERS_VIEW, "View supplier records and material supply terms"),
    (SUPPLIERS_MANAGE, "Create and edit supplier records"),
    (ORDERS_VIEW, "View customer orders"),
    (ORDERS_CREATE, "Create customer orders"),
    (ORDERS_EDIT, "Edit customer orders"),
    (ORDERS_DELETE, "Delete or cancel customer orders"),
    (MRP_VIEW, "View MRP / ATP analysis"),
    (MRP_EXECUTE, "Run MRP calculations"),
    (REPORTS_VIEW, "View daily status and reports"),
    (SEARCH_EXECUTE, "Search across business resources"),
    (SEARCH_MANAGE, "Manage search indexes"),
    (NOTIFY_SEND, "Send and schedule notifications"),
    (NOTIFY_READ, "Read notifications"),
    (NOTIFY_MANAGE, "Manage notification channels and templates"),
    (FILE_UPLOAD, "Upload files to secure storage"),
    (FILE_VIEW, "View and list files"),
    (FILE_DOWNLOAD, "Download files"),
    (FILE_CREATE_VERSION, "Upload new versions of existing files"),
    (FILE_DELETE, "Delete files"),
    (FILE_RESTORE, "Restore deleted files"),
    (FILE_PROCESS, "Trigger AI text extraction on files"),
    (FILE_AI, "Use AI summarize/ask/generate on files"),
]

# Roles per docs/07-security-and-roles.md. Permission sets for modules not
# yet built are included so promoting/demoting a user won't need to change
# once those modules land - only the endpoints enforcing them will.
ROLES: dict[str, dict] = {
    "administrator": {
        "description": "System control - full administrative access",
        "permissions": [code for code, _ in PERMISSIONS],
    },
    "executive": {
        "description": "Business visibility and decisions",
        "permissions": [
            CUSTOMERS_VIEW, PRODUCTS_VIEW, INVENTORY_VIEW, SUPPLIERS_VIEW,
            ORDERS_VIEW, MRP_VIEW, REPORTS_VIEW, SEARCH_EXECUTE, NOTIFY_READ,
            FILE_VIEW, FILE_DOWNLOAD, USERS_VIEW,
        ],
    },
    "operations": {
        "description": "Operational coordination",
        "permissions": [
            CUSTOMERS_VIEW, CUSTOMERS_MANAGE, PRODUCTS_VIEW, INVENTORY_VIEW,
            SUPPLIERS_VIEW, ORDERS_VIEW, ORDERS_CREATE, ORDERS_EDIT,
            MRP_VIEW, REPORTS_VIEW, SEARCH_EXECUTE, SEARCH_MANAGE, NOTIFY_SEND, NOTIFY_READ,
            FILE_UPLOAD, FILE_VIEW, FILE_DOWNLOAD, FILE_CREATE_VERSION,
        ],
    },
    "production": {
        "description": "Production activities",
        "permissions": [
            PRODUCTS_VIEW, INVENTORY_VIEW, ORDERS_VIEW, MRP_VIEW, MRP_EXECUTE,
            REPORTS_VIEW, SEARCH_EXECUTE, NOTIFY_READ, FILE_VIEW, FILE_DOWNLOAD,
        ],
    },
    "procurement": {
        "description": "Supplier and material activities",
        "permissions": [
            SUPPLIERS_VIEW, SUPPLIERS_MANAGE, INVENTORY_VIEW, INVENTORY_ADJUST,
            PRODUCTS_VIEW, MRP_VIEW, REPORTS_VIEW, SEARCH_EXECUTE, SEARCH_MANAGE, NOTIFY_READ,
            FILE_UPLOAD, FILE_VIEW, FILE_DOWNLOAD,
        ],
    },
}

# Roles selectable when a JDK administrator creates a new user.
ASSIGNABLE_ROLES: list[tuple[str, str]] = [
    ("operations", "Operations"),
    ("production", "Production"),
    ("procurement", "Procurement"),
    ("executive", "Executive"),
    ("administrator", "Administrator"),
]


def seed(access: PerenniaAccess) -> None:
    """Idempotently ensure JDK's permissions and roles exist in
    perennia-access. Safe to call on every startup.
    """
    for code, description in PERMISSIONS:
        if access.get_permission(code) is None:
            access.create_permission(code, description)

    for role_code, role_def in ROLES.items():
        if access.get_role(role_code) is None:
            access.create_role(role_code, role_def["description"])

        existing = set(access.get_role_permissions(role_code))
        for perm_code in role_def["permissions"]:
            if perm_code not in existing:
                access.assign_permission_to_role(role_code, perm_code)

    if "administrator" not in access.get_identity_roles(SYSTEM_IDENTITY):
        access.assign_role_to_user(SYSTEM_SUBJECT_ID, "administrator")
