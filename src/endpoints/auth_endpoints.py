from typing import Any
from sanic_ext import openapi
from sanic_jwt import BaseEndpoint
from sanic import json
from sanic.request import Request
from sanic.response import HTTPResponse
from src.services.auth_services import (
    approve_user,
    validate_user_data,
    create_user,
    create_registration_link,
)
from src.shemas.user_shemas import UserData


class Register(BaseEndpoint):
    @openapi.definition(
        body={"application/json": UserData.schema()},
        summary="Endpoint for registration",
    )
    async def post(self, request: Request, *args: Any, **kwargs: Any) -> HTTPResponse:
        data = validate_user_data(request.json)
        user = await create_user(data)
        link = await create_registration_link(user)
        return json({"link": f"127.0.0.1:8000/auth/register/{link}"}, status=201)


class ApproveRegister(BaseEndpoint):
    @openapi.definition(
        summary="Endpoint for approval of registrantion and getting token",
    )
    async def put(
        self, request: Request, link: str, *args: Any, **kwargs: Any
    ) -> HTTPResponse:
        user = await approve_user(link)
        access_token, output = await self.responses.get_access_token_output(
            request, user, self.config, self.instance
        )
        refresh_token = await self.instance.ctx.auth.generate_refresh_token(
            request, user
        )
        output.update({self.config.refresh_token_name(): refresh_token})

        response: HTTPResponse = self.responses.get_token_response(
            request,
            access_token,
            output,
            refresh_token=refresh_token,
            config=self.config,
        )
        return response


register_views = (("/register", Register), ("/register/<link:str>", ApproveRegister))
