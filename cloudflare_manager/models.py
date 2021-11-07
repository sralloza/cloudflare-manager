from ipaddress import IPv4Address
from typing import Union

from pydantic import BaseModel


class DnsRecord(BaseModel):
    id: str
    name: str
    type: str
    content: Union[IPv4Address, str]
    proxied: bool
