from app.common.app import app

__all__ = ["app"]

# debug in IDE
if __name__ == "__main__":
    # import uvicorn
    # from uvicorn.config import LOGGING_CONFIG
    #
    # logging_config = LOGGING_CONFIG.copy()
    # logging_config["formatters"]["access"]["fmt"] = settings.LOG_ACCESS_FORMAT
    # # uvicorn.run(app, host="0.0.0.0")
    # uvicorn.run(app="app:app", host="0.0.0.0", reload=True, log_level="debug",
    #             log_config=logging_config)

    from granian import Granian
    from granian.constants import Interfaces

    server = Granian(
        "common.app:app", interface=Interfaces.ASGI,
        address="0.0.0.0", reload=True,
        log_access=True, log_level="debug"
    )
    server.serve()
