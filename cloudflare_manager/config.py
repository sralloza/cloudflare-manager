import json
from typing import List

from pydantic import BaseSettings, validator


def list_parse_fallback(v):
    try:
        return json.loads(v)
    except Exception:
        return v.split(",")


class Settings(BaseSettings):
    cloudflare_api_key: str
    cloudflare_email: str
    cloudflare_base_api: str = "https://api.cloudflare.com/client/v4"
    telegram_token: str
    telegram_user_id: int
    watched_common_records: List[str] = []
    watched_nocached_records: List[str] = []

    class Config:
        json_loads = list_parse_fallback

    @property
    def known_records(self):
        return self.watched_common_records + self.watched_nocached_records


settings = Settings()
