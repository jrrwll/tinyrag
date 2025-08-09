from app.api import CustomAPIRouter, inner
from app.api import auth, meta, permission, user
from app.api import file, knowledge, workflow, workflow_run
from app.api import model, storage, vector_store, workspace
from app.config import settings

api_router = CustomAPIRouter()
# user & meta
api_router.include_router(auth.router)
api_router.include_router(user.router)
api_router.include_router(permission.router)
api_router.include_router(meta.router)

# resource
api_router.include_router(workspace.router)
api_router.include_router(model.router)
api_router.include_router(vector_store.router)
api_router.include_router(storage.router)

# knowledge
api_router.include_router(file.router)
api_router.include_router(knowledge.router)

# workflow
api_router.include_router(workflow.router)
api_router.include_router(workflow_run.router)

if settings.IS_TEST_ENV:
    api_router.include_router(inner.router)
