from typing import Sequence
from sanic import Sanic
from src.utilities.autodiscovery import autodiscover


def create_app(
    init_blueprints: Sequence[str],
) -> Sanic:
    app = Sanic("TestApp")
    app.config.FALLBACK_ERROR_FORMAT = "json"
    app.ext.openapi.add_security_scheme(
        "token",
        "http",
        scheme="bearer",
        bearer_format="JWT",
    )
    autodiscover(
        app,
        *init_blueprints,
    )
    return app
