from sanic_jwt import Initialize
from sanic import Sanic
from src.endpoints.auth_endpoints import auth_bp
from src.endpoints.goods_endpoints import goods_bp
from src.endpoints.user_endpoints import user_bp
from src.endpoints.transaction_endpoints import transaction_bp
from src.config import SECRET
from src.auth.authentificate import (
    authenticate,
    retrieve_refresh_token,
    retrieve_user,
    store_refresh_token,
)
from src.middleware import container_start, container_finish


def init_auth(app: Sanic) -> None:
    Initialize(
        app,
        authenticate=authenticate,
        store_refresh_token=store_refresh_token,
        retrieve_refresh_token=retrieve_refresh_token,
        retrieve_user=retrieve_user,
        debug=True,
        refresh_token_enabled=True,
        secret=SECRET,
    )


def init_middleware(app: Sanic) -> None:
    app.register_middleware(container_start, "request")
    app.register_middleware(container_finish, "response")  # type:ignore


def create_app() -> Sanic:
    app = Sanic("TestApp")
    app.config.FALLBACK_ERROR_FORMAT = "json"
    app.blueprint(auth_bp)
    app.blueprint(user_bp)
    app.blueprint(goods_bp)
    app.blueprint(transaction_bp)
    return app


def main() -> None:
    app = create_app()
    init_auth(app)
    init_middleware(app)
    app.run(host="0.0.0.0", port=8000, fast=True)
