from sanic_jwt.decorators import protected, inject_user
from sanic_ext import validate
from sanic import Blueprint, json
from sanic.request import Request
from sanic.response import HTTPResponse
from src.exceptions import InvalidUsage
from src.services.goods_services import (
    create_good_instance,
    delete_good_instance,
    get_goods,
    handle_sale,
    update_good_instance,
)
from src.validators import validate_admin_decorator, CommodityData

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


@admin_goods_bp.route("/create", methods=["POST"])
@inject_user()
@protected()
@validate_admin_decorator()
@validate(json=CommodityData)
async def create_good(
    request: Request, user: dict[str, str | int], body: CommodityData
) -> HTTPResponse:
    if set(body.schema()["properties"].keys()) != body.__fields_set__:
        raise InvalidUsage(message="must provide all fields")
    good_id = await create_good_instance(body)
    return json({"message": "good successfuly created", "good_id": good_id}, status=201)


@admin_goods_bp.route("/update/<good_id:int>", methods=["PUT"])
@inject_user()
@protected()
@validate_admin_decorator()
@validate(json=CommodityData)
async def update_good(
    request: Request, user: dict[str, str | int], body: CommodityData, good_id: int
) -> HTTPResponse:
    if body.__fields_set__ == set():
        raise InvalidUsage(message="must provide at least one field")
    await update_good_instance(body, good_id)
    return json("", status=204)


@admin_goods_bp.route("/delete/<good_id:int>", methods=["DELETE"])
@inject_user()
@protected()
@validate_admin_decorator()
async def delete_good(
    request: Request, user: dict[str, str | int], good_id: int
) -> HTTPResponse:
    await delete_good_instance(good_id)
    return json("", status=204)
