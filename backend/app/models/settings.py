from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    """Current application settings.

    The DeepSeek API key is never returned in full - only whether one is
    configured and a short masked preview - so a GET response is safe to
    log or hand to the frontend without leaking the secret. See
    docs on `SETTINGS_MANAGE` in app/permissions/definitions.py.
    """

    # AI / DeepSeek
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_api_key_set: bool = False
    deepseek_api_key_preview: str | None = None

    # AI Assistant behaviour - free text, not validated/parsed here. The
    # assistant reads these at call time to shape its system prompt; JDK
    # itself never interprets their contents.
    assistant_system_prompt: str = ""
    assistant_data_scope: str = ""

    # Production parameters
    batch_size_kg: float = 1000
    daily_capacity_kg: float = 20000
    planning_horizon_days: int = 30
    app_name: str = "JDK Smart Factory"

    # Company letterhead
    company_name: str = ""
    company_address: str = ""
    company_phone: str = ""
    company_email: str = ""
    company_tax_id: str = ""
    company_website: str = ""
    company_logo_attachment_id: str | None = None


class UpdateSettingsRequest(BaseModel):
    """All fields optional - only the ones supplied are changed.

    An empty string for `deepseek_api_key` is treated as "leave unchanged",
    the same convention the Settings UI uses for a masked secret field.
    Use a future dedicated "clear key" action if a hard clear is ever
    needed - this endpoint deliberately can't be used to wipe it by accident.
    """

    deepseek_api_key: str | None = None
    deepseek_model: str | None = None
    deepseek_base_url: str | None = None

    assistant_system_prompt: str | None = None
    assistant_data_scope: str | None = None

    batch_size_kg: float | None = Field(default=None, gt=0)
    daily_capacity_kg: float | None = Field(default=None, gt=0)
    planning_horizon_days: int | None = Field(default=None, gt=0)
    app_name: str | None = None

    company_name: str | None = None
    company_address: str | None = None
    company_phone: str | None = None
    company_email: str | None = None
    company_tax_id: str | None = None
    company_website: str | None = None
    company_logo_attachment_id: str | None = None
