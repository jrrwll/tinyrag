from fastapi import FastAPI

app = FastAPI()
app.openapi()

if __name__ == "__main__":
    from granian import Granian
    from granian.constants import Interfaces

    server = Granian(app, interface=Interfaces.ASGI,
                     address="0.0.0.0",
                     reload=False,
                     log_level="debug",
                     workers=1)
    server.serve()
