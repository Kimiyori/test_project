from functools import wraps
from typing import Any, Awaitable, Callable, Coroutine, ParamSpec, TypeVar
from pydantic import BaseModel, validator, root_validator
from Crypto.Hash import SHA1
from sanic import HTTPResponse
from src.config import SECRET
from src.exceptions import Forbidden
from src.services.user_services import validate_admin


class UserData(BaseModel):
    """Validate user data during registeration"""

    username: str
    password: str

    @validator("username")
    @classmethod
    def length_name(cls, value: str) -> str:
        if 8 < len(value) > 50:
            raise ValueError("name must me in range from 8 to 50")
        return value

    @validator("password")
    @classmethod
    def length_pass(cls, value: str) -> str:
        if 8 < len(value) > 36:
            raise ValueError("password must me in range from 8 to 36")
        return value


class WebHook(BaseModel):
    """Validate data for webhook"""

    signature: str
    transaction_id: str
    user_id: int
    account_id: str
    amount: int

    @root_validator
    @classmethod
    def signature_validate(cls, values: dict[str, str | int]) -> dict[str, str | int]:
        code = (
            f"{SECRET}:"
            f"{values['transaction_id']}:"
            f"{values['user_id']}:"
            f"{values['account_id']}:"
            f"{values['amount']}"
        )
        guessed_signature = SHA1.new()
        guessed_signature.update(code.encode())
        if guessed_signature.hexdigest() != values["signature"]:
            raise ValueError("Invalid signature")
        return values


VaalidateDecoratorParams = ParamSpec("VaalidateDecoratorParams")
VaalidateDecorator = TypeVar("VaalidateDecorator")


def validate_admin_decorator() -> Callable[
    [Callable[VaalidateDecoratorParams, Awaitable[HTTPResponse]]],
    Callable[VaalidateDecoratorParams, Coroutine[Any, Any, HTTPResponse]],
]:
    def decorator(
        func: Callable[VaalidateDecoratorParams, Awaitable[HTTPResponse]]
    ) -> Callable[VaalidateDecoratorParams, Coroutine[Any, Any, HTTPResponse]]:
        @wraps(func)
        async def decorated_function(
            *args: VaalidateDecoratorParams.args,
            **kwargs: VaalidateDecoratorParams.kwargs,
        ) -> HTTPResponse:
            assert isinstance(kwargs["user"]["user_id"], int)  # type: ignore
            if not await validate_admin(kwargs["user"]["user_id"]):  # type: ignore
                raise Forbidden
            response = await func(*args, **kwargs)
            return response

        return decorated_function

    return decorator
