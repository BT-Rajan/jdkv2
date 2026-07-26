"""Builds the shared perennia-crud CrudConfig from JDK's own Settings.

One config, reused by every domain module that adopts perennia-crud
(customers, suppliers, raw materials, products, employees), so connection
pooling/retry/timeout behavior stays consistent across all of them.
"""
from perennia_crud import CrudConfig, DatabaseConfig

from app.core.config import Settings


def build_crud_config(settings: Settings) -> CrudConfig:
    return CrudConfig(
        database=DatabaseConfig(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
        ),
        default_page_size=20,
        max_page_size=100,
        max_connect_retries=2,
        retry_backoff_seconds=0.2,
    )
