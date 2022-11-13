from sanic import Sanic
from src.middleware import container_start, container_finish


def init_middleware(app: Sanic) -> None:
    app.register_middleware(container_start, "request")
    app.register_middleware(container_finish, "response")  # type:ignore
