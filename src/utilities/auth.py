from sanic_jwt import Initialize
from sanic import Sanic
from src.config import SECRET
from src.auth.authentificate import (
    authenticate,
    retrieve_refresh_token,
    retrieve_user,
    store_refresh_token,
)


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
