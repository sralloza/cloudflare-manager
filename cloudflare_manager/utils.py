"""Utils module."""

from ipaddress import IPv4Address

import requests


def get_current_ip() -> IPv4Address:
    """Returns the current IPv4 using the httpbin API."""
    return IPv4Address(requests.get("https://httpbin.org/ip").json()["origin"])
