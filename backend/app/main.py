import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from perennia_auth import PerenniaAuthError
from perennia_access import AccessError

from app.core.errors import AppError, resolve
from app.core.security import settings, access, search
from app.core.search_providers import register_all as register_search_providers
from app.permissions import definitions as permission_definitions
from app.api import auth, users, customers, inventory, suppliers, products, orders, mrp, reports, attachments

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jdk")

app = FastAPI(title="JDK Manufacturing Operations Platform API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(customers.router)
app.include_router(inventory.router)
app.include_router(suppliers.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(mrp.router)
app.include_router(reports.router)
app.include_router(attachments.router)


@app.on_event("startup")
def seed_permissions() -> None:
    permission_definitions.seed(access)
    logger.info("Permission and role seed complete.")
    register_search_providers(search)
    logger.info("Search provider registration complete.")


def _error_response(code: str) -> JSONResponse:
    spec = resolve(code)
    return JSONResponse(status_code=spec.http_status, content={"error": {"code": code, "message": spec.message}})


@app.exception_handler(AppError)
def handle_app_error(request: Request, exc: AppError):
    return _error_response(exc.code)


@app.exception_handler(PerenniaAuthError)
def handle_auth_error(request: Request, exc: PerenniaAuthError):
    return _error_response(getattr(exc, "code", "auth_error"))


@app.exception_handler(AccessError)
def handle_access_error(request: Request, exc: AccessError):
    code = getattr(exc, "code", "access_error")
    if code in ("permission_not_found", "role_not_found", "invalid_access_configuration"):
        logger.error("Access configuration error: %s", exc)
    return _error_response(code)


@app.exception_handler(RequestValidationError)
def handle_validation_error(request: Request, exc: RequestValidationError):
    return _error_response("validation_error")


@app.exception_handler(StarletteHTTPException)
def handle_http_exception(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return _error_response("not_found")
    spec = resolve("http_error")
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": "http_error", "message": spec.message}})


@app.exception_handler(Exception)
def handle_unexpected_error(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return _error_response("internal_error")


@app.get("/api/health")
def health():
    return {"status": "ok"}
