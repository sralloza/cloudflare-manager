"""Cloudflare Manager's config."""

from json import JSONDecodeError, loads
from typing import List

from pydantic import BaseSettings


def list_parse_fallback(v):
    """Enables csv like lists as well as json lists."""
    try:
        return loads(v)
    except JSONDecodeError:
        return v.split(",")


class Settings(BaseSettings):
    """Cloudflare Manager's settings."""

    cloudflare_api_key: str
    cloudflare_email: str
    cloudflare_base_api: str = "https://api.cloudflare.com/client/v4"
    telegram_token: str
    telegram_user_id: int
    watched_common_records: List[str] = []
    watched_nocached_records: List[str] = []

    # pylint: disable=missing-class-docstring,too-few-public-methods
    class Config:
        json_loads = list_parse_fallback

    @property
    def known_records(self):
        """Returns all the known DNS records."""
        return self.watched_common_records + self.watched_nocached_records


settings = Settings()
