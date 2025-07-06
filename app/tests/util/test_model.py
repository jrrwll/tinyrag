from pydantic import Field

from app.util.model import create_model_type


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
