from sanic_jwt.decorators import protected, inject_user
from sanic import Blueprint, json
from sanic.request import Request
from sanic.response import HTTPResponse
from src.exceptions import InvalidUsage, NotFoundInstance
from src.services.user_services import (
    get_user,
    get_user_accounts,
    get_user_transactions,
    get_users,
    set_user_status,
)
from src.validators import validate_admin_decorator

user_bp = Blueprint("users", url_prefix="/user")

admin_bp = Blueprint("admins", url_prefix="/admin")


@user_bp.route("/accounts")
@inject_user()
@protected()
async def user_accounts(request: Request, user: dict[str, str | int]) -> HTTPResponse:
    assert isinstance(user["user_id"], int)
    accounts_dict = await get_user_accounts(user["user_id"])
    return json(accounts_dict)


@user_bp.route("/transactions")
@inject_user()
@protected()
async def user_transactions(
    request: Request, user: dict[str, str | int]
) -> HTTPResponse:
    assert isinstance(user["user_id"], int)
    transactions_dict = await get_user_transactions(user["user_id"])
    return json(transactions_dict)


@admin_bp.route("/users")
@inject_user()
@protected()
@validate_admin_decorator()
async def get_all_users(request: Request, user: dict[str, str | int]) -> HTTPResponse:
    users = await get_users()
    return json(users)


@admin_bp.route("/change_user_status/<status:str>/<user_id:int>")
@inject_user()
@protected()
@validate_admin_decorator()
async def change_user_status(
    request: Request, user: dict[str, str | int], status: str, user_id: int
) -> HTTPResponse:
    print(status)
    if status not in ("disable", "enable"):
        raise InvalidUsage("must be set either 'enable' or 'disable' in url")
    user_that_needs_disable = await get_user(user_id)
    if user_that_needs_disable is None:
        raise NotFoundInstance
    msg = await set_user_status(status, user_that_needs_disable)
    return json({"message": msg})
