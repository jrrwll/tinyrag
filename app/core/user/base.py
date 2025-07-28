from datetime import datetime
from typing import Any

from pydantic import BaseModel


class TokenPayload(BaseModel):
    exp: datetime
    sub: str | Any
    nbf: datetime | None = None
