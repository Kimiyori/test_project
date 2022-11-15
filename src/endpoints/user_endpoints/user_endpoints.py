from sanic_ext import openapi
from sanic_jwt.decorators import protected, inject_user
from sanic import Blueprint, json
from sanic.request import Request
from sanic.response import HTTPResponse
from src.services.user_services import (
    get_user_accounts,
    get_user_transactions,
)

user_bp = Blueprint("users", url_prefix="/users")


@user_bp.route("/accounts")
@openapi.definition(
    summary="Get user's accounts",
)
@inject_user()
@protected()
async def user_accounts(request: Request, user: dict[str, str | int]) -> HTTPResponse:
    assert isinstance(user["user_id"], int)
    accounts_dict = await get_user_accounts(user["user_id"])
    return json(accounts_dict)


@user_bp.route("/transactions")
@openapi.definition(
    summary="Get all user's transactions",
)
@inject_user()
@protected()
async def user_transactions(
    request: Request, user: dict[str, str | int]
) -> HTTPResponse:
    assert isinstance(user["user_id"], int)
    transactions_dict = await get_user_transactions(user["user_id"])
    return json(transactions_dict)
