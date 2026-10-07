from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SapinSettingsView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str
    aes_key_ctr_configured: bool
    aes_iv_ctr_configured: bool
    aes_key_cbc_configured: bool
