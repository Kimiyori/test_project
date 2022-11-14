from sanic_ext import openapi
from sanic_jwt.decorators import protected
from sanic import Blueprint, json
from sanic.request import Request
from sanic.response import HTTPResponse
from src.services.transaction_services import add_amount, validate_webhook_data
from src.shemas.transactions_shemas import WebHook

transaction_bp = Blueprint("transaction", url_prefix="/transactions")


@transaction_bp.route("/payment/webhook", methods=["POST"])
@openapi.definition(
    body={"application/json": WebHook.schema()},
    summary="Deposit money on the account",
)
@protected()
async def account_replenishment(request: Request) -> HTTPResponse:
    data = validate_webhook_data(request.json)
    new_balance = await add_amount(data)
    return json(
        {
            "msg": "money has been successfully credited to the account",
            "new_balance": new_balance,
        }
    )
