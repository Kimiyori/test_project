from sanic_jwt.decorators import protected, inject_user
from sanic_ext import validate
from sanic import Blueprint, json
from sanic.request import Request
from sanic.response import HTTPResponse
from src.services.goods_services import (
    create_good_instance,
    delete_good_instance,
    get_goods,
    handle_sale,
    update_good_instance,
)
from src.shemas.goods_shemas import CommodityCreate, CommodityUpdate
from src.decorators import validate_admin_decorator, validate_exceptions

goods_bp = Blueprint("goods", url_prefix="/goods")

admin_goods_bp = Blueprint("admin_goods", url_prefix="/admin/goods")


@goods_bp.route("/")
@protected()
async def goods_list(request: Request) -> HTTPResponse:
    lst = await get_goods()
    return json(lst)


@goods_bp.route("/buy/<good_id:int>", methods=["POST"])
@inject_user()
@protected()
async def sale_good(
    request: Request, user: dict[str, int], good_id: int
) -> HTTPResponse:
    account_id = request.json["account_id"]
    user_id: int = user["user_id"]
    await handle_sale(account_id, user_id, good_id)
    return json({"msg": "successful"})


@admin_goods_bp.route("/", methods=["POST"])
@inject_user()
@protected()
@validate_admin_decorator()
@validate_exceptions()
@validate(json=CommodityCreate)
async def create_good(
    request: Request, user: dict[str, str | int], body: CommodityCreate
) -> HTTPResponse:
    good_id = await create_good_instance(body)
    return json({"message": "good successfuly created", "good_id": good_id}, status=201)


@admin_goods_bp.route("/<good_id:int>", methods=["PATCH"])
@inject_user()
@protected()
@validate_admin_decorator()
@validate_exceptions()
@validate(json=CommodityUpdate)
async def update_good(
    request: Request, user: dict[str, str | int], body: CommodityUpdate, good_id: int
) -> HTTPResponse:
    await update_good_instance(good_id, body)
    return json("", status=204)


@admin_goods_bp.route("/<good_id:int>", methods=["DELETE"])
@inject_user()
@protected()
@validate_admin_decorator()
async def delete_good(
    request: Request, user: dict[str, str | int], good_id: int
) -> HTTPResponse:
    await delete_good_instance(good_id)
    return json("", status=204)
