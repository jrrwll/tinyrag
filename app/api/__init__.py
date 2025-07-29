from fastapi.routing import APIRouter


class CustomAPIRouter(APIRouter):

    def add_api_route(self, *args, **kwargs):
        kwargs["response_model_exclude_none"] = True
        super().add_api_route(*args, **kwargs)
