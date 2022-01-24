from ipaddress import IPv4Address
from typing import List

from requests.models import HTTPError

from pydantic import parse_obj_as
from requests import Session

from .config import settings
from .models import DnsRecord
from .notify import Notify
from .utils import get_current_ip


class AutoCloudflare:
    def __init__(self):
        self.session = Session()
        self.login()
        self.zone_id: str = self.get_zone_id()

    def login(self):
        self.session.headers.update(
            {
                "X-Auth-Email": settings.cloudflare_email,
                "X-Auth-Key": settings.cloudflare_api_key,
            }
        )

    def get(self, url: str, **kwargs):
        return self.session.get(settings.cloudflare_base_api + url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.session.post(settings.cloudflare_base_api + url, **kwargs)

    def put(self, url: str, **kwargs):
        return self.session.put(settings.cloudflare_base_api + url, **kwargs)

    def get_zone_id(self):
        response = self.get("/zones")
        try:
            response.raise_for_status()
        except HTTPError:
            print(response.text)
            raise

        zones = response.json()["result"]
        if len(zones) != 1:
            raise ValueError(f"Found more than 1 zone: {zones}")

        return zones[0]["id"]

    def get_dns_records(self):
        response = self.get(f"/zones/{self.zone_id}/dns_records")
        return parse_obj_as(List[DnsRecord], response.json()["result"])

    def update_record(
        self, record: DnsRecord, ip: IPv4Address = None, proxied: bool = None
    ):
        data = {"type": record.type, "name": record.name, "ttl": 1}

        if ip is not None:
            data["content"] = str(ip)
        else:
            data["content"] = str(record.content)

        if proxied is not None:
            data["proxied"] = proxied

        response = self.put(f"/zones/{self.zone_id}/dns_records/{record.id}", json=data)
        response.raise_for_status()

    def edit_records(self):
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
                    self.update_record(record, ip=current_ip)

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
    ac = AutoCloudflare()
    ac.edit_records()
