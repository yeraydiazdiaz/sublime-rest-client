from typing import Optional, Mapping
from urllib.parse import urlparse

from dataclasses import dataclass


@dataclass
class Request:
    url: str
    method: str = "GET"
    headers: Optional[Mapping[str, str]] = None
    body: Optional[str] = None

    @property
    def host(self) -> str:
        return urlparse(self.url).netloc
