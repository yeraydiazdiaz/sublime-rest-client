import typing as tp

from dataclasses import dataclass


@dataclass
class Request:
    url: str
    method: str = "GET"
    headers: tp.Mapping[str, str] = None
    body: str = None
