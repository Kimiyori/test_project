from uuid import UUID
from sanic import Blueprint, json
from sanic.request import Request
from sanic.response import HTTPResponse
from src.services.auth_services import (
    approve_user,
    validate_user_data,
    create_user,
    create_registration_link,
)

auth_bp = Blueprint("auth")


@auth_bp.route("/registration", methods=["POST"])
async def registration(request: Request) -> HTTPResponse:
    data = validate_user_data(request.json)
    user = await create_user(data)
    link = await create_registration_link(user)
    return json({"link": f"127.0.0.1:8000/registration/{link}"}, status=201)


@auth_bp.route("/registration/<link:uuid>", methods=["POST"])
async def approve_registration(request: Request, link: UUID) -> HTTPResponse:
    user = await approve_user(link)
    return json({"username": user.username, "password": user.password}, status=200)
