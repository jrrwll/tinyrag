from app.core.rag.api import KnowledgeStreamChatPublic
from app.util.api import ApiResult


def test_api():
    res = ApiResult.create(KnowledgeStreamChatPublic(answer='Hi'))
    print(f"\nres={res}")
    print(f"\nres={res.model_dump_json()}")
