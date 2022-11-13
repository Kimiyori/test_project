from sanic_ext import openapi
from sanic_jwt.decorators import protected, inject_user
from sanic import Blueprint, json
from sanic.request import Request
from sanic.response import HTTPResponse
from src.services.goods_services import (
    get_goods,
    handle_sale,
)

goods_bp = Blueprint("goods", url_prefix="/goods")


@goods_bp.route("/")
@openapi.definition(
    summary="Get list of all goods",
)
@protected()
async def goods_list(request: Request) -> HTTPResponse:
    lst = await get_goods()
    return json(lst)


@goods_bp.route("/buy/<good_id:int>", methods=["POST"])
@openapi.definition(
    summary="Get item",
)
@inject_user()
@protected()
async def sale_good(
    request: Request, user: dict[str, int], good_id: int
) -> HTTPResponse:
    account_id = request.json["account_id"]
    user_id: int = user["user_id"]
    await handle_sale(account_id, user_id, good_id)
    return json({"msg": "successful"})
