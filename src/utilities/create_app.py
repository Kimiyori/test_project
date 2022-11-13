from types import ModuleType
from sanic import Sanic
from src.utilities.autodiscovery import autodiscover


def create_app(
    init_blueprints: ModuleType | str,
) -> Sanic:
    app = Sanic("TestApp")
    app.config.FALLBACK_ERROR_FORMAT = "json"
    autodiscover(
        app,
        init_blueprints,
        recursive=True,
    )
    return app
