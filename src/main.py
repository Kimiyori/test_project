from src.utilities.create_app import create_app
from src.utilities.auth import init_auth
from src.utilities.middleware import init_middleware

blueprints = [
    "src.endpoints.goods_endpoints.goods_endpoints",
    "src.endpoints.user_endpoints.user_endpoints",
    "src.endpoints.transaction_endpoints",
    "src.endpoints.auth_endpoints",
    "src.endpoints.user_endpoints.admin_user_endpoints",
    "src.endpoints.goods_endpoints.admin_good_endpoints",
]


def main() -> None:
    app = create_app(blueprints)
    init_auth(app)
    init_middleware(app)
    app.run(host="0.0.0.0", port=8000, fast=True)
