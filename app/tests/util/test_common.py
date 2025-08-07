from contextlib import AbstractContextManager
from typing import Self
from random import randint
import traceback
from app.core.knowledge.api import KnowledgeStreamChatPublic
from app.core.user.enums import UserRole
from app.util.api import ApiResult


def test_model():
    res = ApiResult.create(KnowledgeStreamChatPublic(answer='Hi'))
    print(f"\nres={res}")
    print(f"\nres={res.model_dump_json(exclude_none=True)}")


def test_enum():
    print("\ntest_enum")
    for m in UserRole:
        print(f"{m.name} level = {m.level}")

    for m in UserRole:
        for n in UserRole:
            print(f"{m.name} implies {n.name} = {m.implies(n)}")


class MyContextManager(AbstractContextManager):

    def __enter__(self) -> int:
        return randint(0, 10)

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: object | None,
    ) -> None:
        if not exc_type:
            return
        msg = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
        print(f"msg:\n{msg}")


def test_contextlib():
    with MyContextManager() as x:
        print(f"\nx={x}")

    try:
        with MyContextManager() as x:
            print(f"\nx={x}")
            raise ValueError("x is too big")
    except Exception as e:
        print(f"\nException handled: {type(e)} {e}")
