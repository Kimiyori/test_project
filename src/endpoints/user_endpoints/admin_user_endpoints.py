from sanic_ext import validate, openapi
from sanic_jwt.decorators import protected, inject_user
from sanic import json
from sanic.request import Request
from sanic.response import HTTPResponse
from src.exceptions import NotFoundInstance
from src.services.user_services import (
    get_user,
    get_users,
    set_user_status,
)
from src.decorators import validate_admin_decorator
from src.endpoints.admin import admin_bp as admin_user_bp
from src.shemas.user_shemas import ChangeUserStatus


@admin_user_bp.route("/users/status", methods=["PATCH"])
@openapi.definition(
    body={"application/json": ChangeUserStatus.schema()},
    summary="Change user status",
)
@inject_user()
@protected()
@validate_admin_decorator()
@validate(json=ChangeUserStatus)
async def change_user_status(
    request: Request, user: dict[str, str | int], body: ChangeUserStatus
) -> HTTPResponse:
    user_that_needs_change_status = await get_user(body.id)
    if user_that_needs_change_status is None:
        raise NotFoundInstance
    msg = await set_user_status(body.status, user_that_needs_change_status)
    return json({"message": msg})


@admin_user_bp.route("/users")
@openapi.definition(
    summary="Get all users with teir accounts",
)
@inject_user()
@protected()
@validate_admin_decorator()
async def get_all_users(request: Request, user: dict[str, str | int]) -> HTTPResponse:
    users = await get_users()
    return json(users)
