from ipaddress import IPv4Address

import requests


def get_current_ip():
    return IPv4Address(requests.get("https://httpbin.org/ip").json()["origin"])
