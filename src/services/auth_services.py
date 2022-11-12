from __future__ import annotations
import uuid
from pydantic import ValidationError
from dependency_injector.wiring import Provide, inject, Closing
from redis.asyncio.client import Redis
from src.containers import Container
from src.db.data_acess_layer.user import UserDAO
from src.db.models import UserTable
from src.exceptions import InvalidUsage, NotFoundInstance
from src.validators import UserData


def validate_user_data(data: dict[str, int]) -> UserData:
    try:
        validated_data = UserData(**data)
    except ValidationError as error:
        raise InvalidUsage(message=error.errors()[0]["msg"]) from error
    except TypeError as error:
        raise InvalidUsage(message="must provide username and password") from error
    return validated_data


@inject
async def create_user(
    data: UserData,
    user_session: UserDAO = Closing[Provide[Container.user_session]],
) -> int:
    user = user_session.create(username=data.username, password=data.password)
    user_session.add(user)
    await user_session.session.flush()
    user_id: int = user.id
    await user_session.commit()
    return user_id


@inject
async def create_registration_link(
    user_id: int,
    redis_session: Redis[bytes] = Closing[Provide[Container.redis_session]],
) -> str:
    link = uuid.uuid4().hex
    await redis_session.set(str(link), user_id)
    return link


@inject
async def approve_user(
    link: uuid.UUID,
    user_session: UserDAO = Closing[Provide[Container.user_session]],
    redis_session: Redis[bytes] = Closing[Provide[Container.redis_session]],
) -> UserTable:
    user_id = await redis_session.get(str(link.hex))
    await redis_session.delete(str(link.hex))
    user = await user_session.conf_new_user(id=int(user_id))  # type: ignore
    if user is None:
        raise NotFoundInstance
    await user_session.commit()
    return user
