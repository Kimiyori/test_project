from typing import Any
import redis.asyncio as redis
from dependency_injector import containers, providers, resources
from src.db.data_acess_layer.account import AccountDAO
from src.db.data_acess_layer.goods import GoodsDAO
from src.db.data_acess_layer.transactions import TransactionDAO
from src.db.data_acess_layer.user import UserDAO
from src.db.session import session_factory


class RedisResource(resources.Resource):  # type:ignore
    def init(self, *args: Any, **kwargs: Any):  # type:ignore
        rds = redis.from_url("redis://redis:6379")
        return rds

    async def shutdown(  # type:ignore  # pylint: disable=invalid-overridden-method
        self, resource, *args: Any, **kwargs: Any
    ):
        await resource.close()


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["src.services", "src.auth"]
    )
    redis_session = providers.Resource(RedisResource)
    session = providers.Resource(session_factory)
    user_session = providers.Factory(UserDAO, session)
    goods_session = providers.Factory(GoodsDAO, session)
    account_session = providers.Factory(AccountDAO, session)
    transaction_session = providers.Factory(TransactionDAO, session)
