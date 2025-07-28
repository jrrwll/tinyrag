from app.api import CustomAPIRouter, file, inner, knowledge, \
    model, workflow, workflow_run, workspace, user, auth
from app.config import settings

api_router = CustomAPIRouter()
api_router.include_router(user.router)
api_router.include_router(auth.router)
api_router.include_router(workspace.router)
api_router.include_router(model.router)

api_router.include_router(workflow.router)
api_router.include_router(workflow_run.router)

api_router.include_router(knowledge.router)
api_router.include_router(file.router)

if settings.IS_TEST_ENV:
    api_router.include_router(inner.router)
