import typing as tp

from dataclasses import dataclass


@dataclass
class Request:
    url: str
    method: str = "GET"
    headers: tp.Optional[tp.Mapping[str, str]] = None
    body: tp.Optional[str] = None
