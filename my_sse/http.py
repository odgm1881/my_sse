import json
import re

from dataclasses import dataclass
from collections import namedtuple

from typing import Any, Callable, Awaitable, AsyncGenerator


StatusCode = namedtuple("StatusCode", ("num_stat", "msg_stat"))


@dataclass
class Request:
    method: str
    url: str
    query: dict | None = None
    path_params: dict | None = None
    content_length: int | None = None
    content_type: str | None = None
    body: Any | None = None


@dataclass
class Response:
    status: StatusCode
    connection: str
    content_type: str | None = None
    body: Any | None = None


@dataclass
class Router:
    url_pattern: str
    method: str
    endpoint: Callable[[Request], Awaitable[Any] | AsyncGenerator[Any, None]]
    is_sse: bool = False

    def __post_init__(self):
        pattern = re.sub(r"\{(\w+)\}", r"(?P<\1>[^/]+)", self.url_pattern)
        self.regex = re.compile(f"^{pattern}$")

    def match(self, url: str) -> dict | None:
        match = self.regex.match(url)
        if match:
            return match.groupdict()
        return None


class SSEResponse:
    def __init__(self, data: Any):
        if isinstance(data, dict | list):
            self.data = json.dumps(data)
        elif data is None:
            self.data = ""
        else:
            self.data = str(data)

    def to_bytes(self):
        return self.data.encode()
