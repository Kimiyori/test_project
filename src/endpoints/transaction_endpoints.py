from sanic import Blueprint, json
from sanic.request import Request
from sanic.response import HTTPResponse
from src.services.transaction_services import add_amount, validate_webhook_data
from sanic_jwt.decorators import protected

transaction_bp = Blueprint("transaction")


@transaction_bp.route("/payment/webhook", methods=["POST"])
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
