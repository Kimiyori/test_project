from __future__ import annotations
import uuid
import bcrypt
from pydantic import ValidationError
from dependency_injector.wiring import Provide, inject, Closing
from redis.asyncio.client import Redis
from src.containers import Container
from src.db.data_acess_layer.user import UserDAO
from src.exceptions import InvalidUsage
from src.shemas.user_shemas import UserData


def validate_user_data(data: dict[str, int]) -> UserData:
    try:
        validated_data = UserData(**data)
    except ValidationError as error:
        raise InvalidUsage(message=error.errors()[0]["msg"]) from error
    except TypeError as error:
        raise InvalidUsage(message="must provide username and password") from error
    return validated_data


def generate_password_hash(password: str) -> str:
    password_bin = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bin, bcrypt.gensalt())
    return hashed.decode("utf-8")


def check_password_hash(plain_password: str, password_hash: str) -> bool:
    plain_password_bin = plain_password.encode("utf-8")
    password_hash_bin = password_hash.encode("utf-8")
    is_correct = bcrypt.checkpw(plain_password_bin, password_hash_bin)
    return is_correct


@inject
async def create_user(
    data: UserData,
    user_session: UserDAO = Closing[Provide[Container.user_session]],
) -> int:
    user = user_session.create(
        username=data.username, password=generate_password_hash(data.password)
    )
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
    link: str,
    user_session: UserDAO = Closing[Provide[Container.user_session]],
    redis_session: Redis[bytes] = Closing[Provide[Container.redis_session]],
) -> dict[str, int | str] | None:
    user_id_b = await redis_session.get(str(link))
    user_id: int = int(user_id_b)  # type: ignore
    await user_session.conf_new_user(user_id)
    await user_session.commit()
    await redis_session.delete(str(link))
    return {"user_id": user_id}
