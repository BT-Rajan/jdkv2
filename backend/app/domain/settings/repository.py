from app.core.database import Database

# The keys this repository is willing to read/write in factory_config.
# Keeping an explicit allow-list here (rather than trusting caller input)
# means a bug elsewhere can never turn this into an arbitrary key/value
# writer against a shared config table other code also reads.
_KNOWN_KEYS = {
    "deepseek_api_key",
    "deepseek_model",
    "deepseek_base_url",
    "assistant_system_prompt",
    "assistant_data_scope",
    "batch_size_kg",
    "daily_production_capacity_kg",
    "planning_horizon_days",
    "app_name",
    "company_name",
    "company_address",
    "company_phone",
    "company_email",
    "company_tax_id",
    # Legacy key, superseded by company_tax_id - kept readable (never
    # written to) so pre-rename values still surface as a fallback. See
    # SettingsService.get().
    "company_gstin",
    "company_website",
    "company_logo_attachment_id",
}


class SettingsRepository:
    """Reads/writes app-wide configuration in the shared `factory_config`
    key/value table (see backend/sql/schema.sql). Values are stored as text;
    type coercion happens in the service layer.
    """

    def __init__(self, db: Database):
        self._db = db

    def get_all(self) -> dict[str, str]:
        with self._db.cursor() as cur:
            cur.execute(
                "SELECT key_name, val FROM factory_config WHERE key_name IN %s",
                (tuple(_KNOWN_KEYS),),
            )
            return {row["key_name"]: row["val"] for row in cur.fetchall()}

    def set_many(self, values: dict[str, str]) -> None:
        unknown = set(values) - _KNOWN_KEYS
        if unknown:
            raise ValueError(f"Unknown settings key(s): {sorted(unknown)}")
        if not values:
            return
        with self._db.transaction() as cur:
            cur.executemany(
                """
                INSERT INTO factory_config (key_name, val) VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE val = VALUES(val)
                """,
                list(values.items()),
            )
