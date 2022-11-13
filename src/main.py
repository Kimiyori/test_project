import src.endpoints as blueprints
from src.utilities.create_app import create_app
from src.utilities.auth import init_auth
from src.utilities.middleware import init_middleware


def main() -> None:
    app = create_app(blueprints)
    init_auth(app)
    init_middleware(app)
    app.run(host="0.0.0.0", port=8000, fast=True)
