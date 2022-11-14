from __future__ import annotations
from typing import Any
from sanic_jwt import exceptions
from redis.asyncio.client import Redis
from dependency_injector.wiring import Provide, inject, Closing
from sanic import Request
from src.containers import Container
from src.db.data_acess_layer.user import UserDAO
from src.services.auth_services import check_password_hash


# Authentication
@inject
async def authenticate(
    request: Request,
    user_session: UserDAO = Closing[Provide[Container.user_session]],
    *args: Any,
    **kwargs: Any,
) -> dict[str, int | None]:
    if request.json is None:
        raise exceptions.AuthenticationFailed("missing payload")

    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username or not password:
        raise exceptions.AuthenticationFailed("Missing username or password")

    user = await user_session.get(username=username)

    if user is None:
        raise exceptions.AuthenticationFailed("User not found.")
    if not user_session.check_status(user):
        raise exceptions.AuthenticationFailed("User don't confrim account")
    assert isinstance(user.password, str)
    if not check_password_hash(password, user.password):
        raise exceptions.AuthenticationFailed("Wrong password")
    data = {
        "user_id": user.id,
    }
    return data


@inject
async def store_refresh_token(
    user_id: int,
    refresh_token: str,
    redis_session: Redis[bytes] = Closing[Provide[Container.redis_session]],
    *args: Any,
    **kwargs: Any,
) -> None:
    key = f"refresh_token_{user_id}"
    await redis_session.set(key, refresh_token)


@inject
async def retrieve_refresh_token(
    request: Request,
    user_id: int,
    redis_session: Redis[bytes] = Closing[Provide[Container.redis_session]],
    *args: Any,
    **kwargs: Any,
) -> bytes | None:
    key = f"refresh_token_{user_id}"
    refresh_token: bytes | None = await redis_session.get(key)
    return refresh_token


@inject
async def retrieve_user(
    request: Request,
    payload: Any,
    user_session: UserDAO = Closing[Provide[Container.user_session]],
    *args: Any,
    **kwargs: Any,
) -> dict[str, int | str] | None:
    if payload:
        user_id = payload.get("user_id", None)
        user = await user_session.get(id=user_id)
        if not user:
            return None
        assert isinstance(user.id, int)
        assert isinstance(user.username, str)
        return {"user_id": user.id, "username": user.username}
    return None
