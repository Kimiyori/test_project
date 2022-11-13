from sanic_jwt.decorators import protected, inject_user
from sanic import json
from sanic.request import Request
from sanic.response import HTTPResponse
from src.exceptions import InvalidUsage, NotFoundInstance
from src.services.user_services import (
    get_user,
    get_users,
    set_user_status,
)
from src.decorators import validate_admin_decorator
from src.endpoints.admin import admin_bp as admin_user_bp


@admin_user_bp.route("/change_user_status/<status:str>/<user_id:int>")
@inject_user()
@protected()
@validate_admin_decorator()
async def change_user_status(
    request: Request, user: dict[str, str | int], status: str, user_id: int
) -> HTTPResponse:
    if status not in ("disable", "enable"):
        raise InvalidUsage("must be set either 'enable' or 'disable' in url")
    user_that_needs_disable = await get_user(user_id)
    if user_that_needs_disable is None:
        raise NotFoundInstance
    msg = await set_user_status(status, user_that_needs_disable)
    return json({"message": msg})


@admin_user_bp.route("/users")
@inject_user()
@protected()
@validate_admin_decorator()
async def get_all_users(request: Request, user: dict[str, str | int]) -> HTTPResponse:
    users = await get_users()
    return json(users)
