"""Main module."""

from ipaddress import IPv4Address
from typing import List

from pydantic import parse_obj_as
from requests import Session

from .config import settings
from .models import DnsRecord
from .notify import Notify
from .utils import get_current_ip


class AutoCloudflare:
    """Cloudflare HTTP API Interface."""

    def __init__(self):
        self.session = Session()
        self.login()
        self.zone_id: str = self.get_zone_id()

    def login(self):
        """Sets the HTTP authentication headers."""
        self.session.headers.update(
            {
                "X-Auth-Email": settings.cloudflare_email,
                "X-Auth-Key": settings.cloudflare_api_key,
            }
        )

    def get(self, url: str, **kwargs):
        """Sends a HTTP GET request."""
        return self.session.get(settings.cloudflare_base_api + url, **kwargs)

    def post(self, url: str, **kwargs):
        """Sends a HTTP POST request."""
        return self.session.post(settings.cloudflare_base_api + url, **kwargs)

    def put(self, url: str, **kwargs):
        """Sends a HTTP PUT request."""
        return self.session.put(settings.cloudflare_base_api + url, **kwargs)

    def get_zone_id(self) -> str:
        """Returns the first user's zone ID."""
        response = self.get("/zones")
        zones = response.json()["result"]
        assert len(zones) == 1
        return zones[0]["id"]

    def get_dns_records(self) -> List[DnsRecord]:
        """Returns the zone DNS records."""
        response = self.get(f"/zones/{self.zone_id}/dns_records")
        return parse_obj_as(List[DnsRecord], response.json()["result"])

    def update_record(
        self, record: DnsRecord, ip_v4: IPv4Address = None, proxied: bool = None
    ):
        """Updates a DNS record.

        Args:
            record (DnsRecord): DNS record to update.
            ip_v4 (IPv4Address, optional): IPv4 of the record. If None it will not
                be updated. Defaults to None.
            proxied (bool, optional): represents if the record is proxied or not.
                If None it will not be updated. Defaults to None.
        """

        data = {"type": record.type, "name": record.name, "ttl": 1}

        if ip_v4 is not None:
            data["content"] = str(ip_v4)
        else:
            data["content"] = str(record.content)

        if proxied is not None:
            data["proxied"] = proxied

        response = self.put(f"/zones/{self.zone_id}/dns_records/{record.id}", json=data)
        response.raise_for_status()

    def edit_records(self):
        """Automatically updates all records based on the settings."""

        ips_records = self.get_dns_records()
        current_ip = get_current_ip()

        with Notify() as notify:
            for record in ips_records:
                if record.type != "A":
                    continue

                # Ignored record
                if record.name not in settings.known_records:
                    continue

                if record.content != current_ip:
                    notify(f"Updating `IP={current_ip}` of {record.name!r}")
                    self.update_record(record, ip_v4=current_ip)

                if record.name in settings.watched_nocached_records and record.proxied:
                    notify(f"Updating `proxy=False` of {record.name!r}")
                    self.update_record(record, proxied=False)
                elif (
                    record.name in settings.watched_common_records
                    and not record.proxied
                ):
                    notify(f"Updating `proxy=True` of {record.name!r}")
                    self.update_record(record, proxied=True)


def main():
    """Main function."""
    auto_cloudflare = AutoCloudflare()
    auto_cloudflare.edit_records()
