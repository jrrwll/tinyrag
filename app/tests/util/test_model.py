from typing import Protocol, Self

from corepy.model import create_model_type, extract_validation_error, \
    new_validation_error
from pydantic import BaseModel, Field, ValidationError, field_validator, \
    model_validator
from pydantic_core._pydantic_core import PydanticCustomError

from app.core.knowledge.api import KnowledgePublic


def test_create_dynamic_model():
    fields = {
        "name": (str, Field(..., description="用户全名", min_length=2, max_length=50)),
        "age": (int, Field(gt=0, le=120, description="用户年龄")),
        "email": (str, Field(None, description="用户邮箱",
                             pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")),
        "is_active": (bool, Field(True, description="账户激活状态"))
    }

    UserModel = create_model_type(
        "User",
        fields,
        __doc__="用户信息模型"
    )
    user = UserModel(name="张三", age=30, email="zhangsan@example.com")
    print(f"\nuser={user}")
    print(user.model_json_schema())


class SpeakProtocol(Protocol):
    def say(self) -> str: ...


class Box(BaseModel):
    name: str

    def say(self) -> str:
        return f"I'm {self.name}"


def process[T: BaseModel & SpeakProtocol](obj: T) -> None:
    print(obj.say(), obj.model_dump())


def test_protocol():
    box = Box(name='Box')
    print(f"\nbox: {box}")
    process(box)


def test_model():
    print("\n")
    for field_name, field_info in KnowledgePublic.model_fields.items():
        print(f"{field_name} annotation={field_info.annotation} {field_info}")


def test_extract_validation_error():
    class Some(BaseModel):
        id: int
        name: str = Field(min_length=2, max_length=4)
        age: int = Field(gt=0, le=120)
        score: float
        host: str

        @field_validator("host")
        @staticmethod
        def _validate_host(host: str) -> str:
            if host == '*':
                raise ValueError("host cannot be *")
            return host

    try:
        Some.model_validate({
            "name": "12345",
            "age": -1,
            "score": "no",
            "host": "*"

        })
    except ValidationError as e:
        print(e)
        print(f"\nerrors:\n")
        for err in e.errors():
            print(f"{err}")

        res = extract_validation_error(e)
        print(f"\nres:\n{res}")

        err = new_validation_error(Box(name="x"), ["a", "b"])
        print(f"\nerr:\n{err}")


    class Awesome(BaseModel):
        id: int

        @model_validator(mode="after")
        def _validate(self) -> Self:
            if self.id == 1:
                raise PydanticCustomError(
                    "missing", "Field required",
                )
            elif self.id == 2:
                raise new_validation_error(self, ["a", "b"])
            return self

    try:
        Awesome.model_validate({"id": 1})
    except ValidationError as e:
        print(f"\nAwesome1:\n{e}")

    try:
        Awesome.model_validate({"id": 2})
    except ValidationError as e:
        print(f"\nAwesome2:\n{e}")