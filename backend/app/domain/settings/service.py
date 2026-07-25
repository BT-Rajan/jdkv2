from app.domain.settings.repository import SettingsRepository
from app.models.settings import AppSettings, UpdateSettingsRequest

_DEFAULTS = {
    "deepseek_model": "deepseek-chat",
    "deepseek_base_url": "https://api.deepseek.com",
    "batch_size_kg": "1000",
    "daily_production_capacity_kg": "20000",
    "planning_horizon_days": "30",
    "app_name": "JDK Smart Factory",
    "company_name": "",
    "company_address": "",
    "company_phone": "",
    "company_email": "",
    "company_gstin": "",
    "company_website": "",
}


def _mask(secret: str) -> str:
    """Never reveal the full key - a short prefix/suffix is enough for an
    admin to recognise "yes, that's the key I set" without it being usable
    if the response is ever logged, cached, or shown over someone's shoulder.
    """
    if len(secret) <= 8:
        return "•" * len(secret)
    return f"{secret[:3]}…{secret[-4:]}"


class SettingsService:
    def __init__(self, repo: SettingsRepository):
        self._repo = repo

    def get(self) -> AppSettings:
        raw = {**_DEFAULTS, **self._repo.get_all()}
        api_key = raw.get("deepseek_api_key", "") or ""
        return AppSettings(
            deepseek_model=raw["deepseek_model"],
            deepseek_base_url=raw["deepseek_base_url"],
            deepseek_api_key_set=bool(api_key),
            deepseek_api_key_preview=_mask(api_key) if api_key else None,
            batch_size_kg=float(raw["batch_size_kg"]),
            daily_capacity_kg=float(raw["daily_production_capacity_kg"]),
            planning_horizon_days=int(raw["planning_horizon_days"]),
            app_name=raw["app_name"],
            company_name=raw["company_name"],
            company_address=raw["company_address"],
            company_phone=raw["company_phone"],
            company_email=raw["company_email"],
            company_gstin=raw["company_gstin"],
            company_website=raw["company_website"],
        )

    def update(self, body: UpdateSettingsRequest) -> AppSettings:
        values: dict[str, str] = {}

        # An empty/omitted API key means "leave unchanged" - see
        # UpdateSettingsRequest's docstring. Only a non-empty string writes.
        if body.deepseek_api_key:
            values["deepseek_api_key"] = body.deepseek_api_key.strip()
        if body.deepseek_model is not None:
            values["deepseek_model"] = body.deepseek_model.strip()
        if body.deepseek_base_url is not None:
            values["deepseek_base_url"] = body.deepseek_base_url.strip()

        if body.batch_size_kg is not None:
            values["batch_size_kg"] = str(body.batch_size_kg)
        if body.daily_capacity_kg is not None:
            values["daily_production_capacity_kg"] = str(body.daily_capacity_kg)
        if body.planning_horizon_days is not None:
            values["planning_horizon_days"] = str(body.planning_horizon_days)
        if body.app_name is not None:
            values["app_name"] = body.app_name.strip()

        for field in ("company_name", "company_address", "company_phone",
                      "company_email", "company_gstin", "company_website"):
            incoming = getattr(body, field)
            if incoming is not None:
                values[field] = incoming.strip()

        self._repo.set_many(values)
        return self.get()
