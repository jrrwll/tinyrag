from enum import StrEnum

from pydantic import BaseModel


class HttpMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class HttpConfig(BaseModel):
    method: HttpMethod = HttpMethod.POST
    url: str
    headers: dict[str, str] | None = None
    params: dict[str, str] | None = None
    json_body: str | None = None
