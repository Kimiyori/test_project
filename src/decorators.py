from functools import wraps
from typing import Any, Awaitable, Callable, Coroutine, ParamSpec, TypeVar
from sanic_ext.exceptions import ValidationError
from sanic import HTTPResponse
from src.exceptions import Forbidden, InvalidUsage
from src.services.user_services import validate_admin

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


def validate_exceptions() -> Callable[
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
            try:
                response = await func(*args, **kwargs)
            except ValidationError as error:
                raise InvalidUsage(message=error.__context__) from error  # type: ignore
            return response

        return decorated_function

    return decorator
