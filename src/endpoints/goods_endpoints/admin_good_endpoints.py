from sanic_jwt.decorators import protected, inject_user
from sanic_ext import validate, openapi
from sanic import json
from sanic.request import Request
from sanic.response import HTTPResponse
from src.services.goods_services import (
    create_good_instance,
    delete_good_instance,
    update_good_instance,
)
from src.shemas.goods_shemas import CommodityCreate, CommodityUpdate
from src.decorators import validate_admin_decorator, validate_exceptions
from src.endpoints.admin import admin_bp as admin_goods_bp


@admin_goods_bp.route("/goods", methods=["POST"])
@openapi.definition(
    body={"application/json": CommodityCreate.schema()},
    summary="Create good",
)
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


@admin_goods_bp.route("/goods/<good_id:int>", methods=["PATCH"])
@openapi.definition(
    body={"application/json": CommodityUpdate.schema()},
    summary="Update good data",
)
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


@admin_goods_bp.route("/goods/<good_id:int>", methods=["DELETE"])
@inject_user()
@protected()
@validate_admin_decorator()
async def delete_good(
    request: Request, user: dict[str, str | int], good_id: int
) -> HTTPResponse:
    await delete_good_instance(good_id)
    return json("", status=204)
