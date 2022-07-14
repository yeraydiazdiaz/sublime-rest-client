from typing import Optional, Mapping

from dataclasses import dataclass


@dataclass
class Request:
    url: str
    method: str = "GET"
    headers: Optional[Mapping[str, str]] = None
    body: Optional[str] = None
