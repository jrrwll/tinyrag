from app.core.rag.api import KnowledgeStreamChatPublic
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

