from app.core.model.enums import ModelType
from app.entities.model import Model
from app.schemas.model import ModelCreate, ModelPublic

def test_convert():
    model_create = ModelCreate(name="ollama",
                               type=ModelType.LLM,
                               base_url="http://localhost:11434")
    print(f"model_create:\n{model_create.model_dump()}")

    model = Model(**model_create.model_dump())
    print(f"model:\n{model.model_dump()}")

    model = Model(name="ollama")
    print(f"model:\n{model.model_dump()}")
