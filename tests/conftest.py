import json
from unittest.mock import patch
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import pytest
import pytest_asyncio
from src.config import get_postgres_uri, TEST_DATABASE_NAME
from src.containers import Container
from src.db.base import Base
from sqlalchemy import text
from src.db.data_acess_layer.account import AccountDAO
from src.db.data_acess_layer.transactions import TransactionDAO
from src.db.data_acess_layer.user import UserDAO
from src.db.models import UserStatus, UserType
from src.services.auth_services import generate_password_hash
from src.utilities.auth import init_auth
from src.utilities.create_app import create_app
from src.main import blueprints


@pytest_asyncio.fixture
async def test_engine():
    engine_aux = create_async_engine(
        get_postgres_uri(database_name=False),
        future=True,
    )
    await create_db(engine_aux)
    engine = create_async_engine(
        get_postgres_uri(test=True),
        future=True,
        echo=False,
    )
    try:
        yield engine
    finally:
        await drop_db(engine_aux)


@pytest_asyncio.fixture
async def class_session_factory(test_engine):
    await create_tables(test_engine)
    try:
        yield sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)
    finally:
        await drop_tables(test_engine)


@pytest_asyncio.fixture
async def session_factory(test_engine):
    yield sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def dao_session(class_session_factory):
    async with class_session_factory() as session:
        yield session


async def create_db(engine) -> None:
    async with engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        try:
            await conn.execute(text(f"create database {TEST_DATABASE_NAME}"))
        except sqlalchemy.exc.ProgrammingError:
            await conn.execute(
                text(f"drop database if exists {TEST_DATABASE_NAME} WITH (FORCE)")
            )
            await conn.execute(text(f"create database {TEST_DATABASE_NAME}"))


async def create_tables(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def drop_db(engine) -> None:
    async with engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(
            text(f"drop database if exists {TEST_DATABASE_NAME} WITH (FORCE)")
        )
        await engine.dispose()


@pytest.fixture
def app():
    app = create_app(blueprints)
    init_auth(app)
    app.ctx.container = Container()
    yield app


class FakeRedis:
    def __init__(self) -> None:
        self._storage = dict()

    async def set(self, key, value):
        self._storage[key] = value

    async def get(self, key):
        try:
            value = self._storage[key]
        except KeyError:
            value = None
        return value

    async def delete(self, key):
        del self._storage[key]

    async def close(self):
        pass


@pytest.fixture(scope="session", autouse=True)
def params_user():
    pytest.params = {
        "username": "test_just_user",
        "password": "test_pass_fur_user",
    }


@pytest.fixture(scope="session", autouse=True)
def params_admin():
    pytest.admin_params = {
        "username": "test_admin",
        "password": "test_admin",
    }


@pytest_asyncio.fixture
async def create_user(dao_session):
    user_session = UserDAO(dao_session)
    status = UserStatus.ACTIVE.name
    user = user_session.create(
        status=status,
        username=pytest.params["username"],
        password=generate_password_hash(pytest.params["password"]),
    )
    user_session.add(user)
    await user_session.commit()
    return user.id


@pytest_asyncio.fixture
async def create_admin(dao_session):
    user_session = UserDAO(dao_session)
    status = UserStatus.ACTIVE.name
    type = UserType.ADMIN.name
    user = user_session.create(
        status=status,
        type=type,
        username=pytest.admin_params["username"],
        password=generate_password_hash(pytest.admin_params["password"]),
    )
    user_session.add(user)
    await user_session.commit()
    return user.id


@pytest_asyncio.fixture
async def create_account(create_user, dao_session, balance):
    account_session = AccountDAO(dao_session)
    account = account_session.create(user_id=create_user, balance=balance)
    account_session.add(account)
    await account_session.commit()
    return str(account.id)


@pytest_asyncio.fixture
async def create_transactions(create_user, dao_session, create_account):
    transaction_session = TransactionDAO(dao_session)
    transaction1 = transaction_session.create(account_id=create_account, amount=11)
    transaction2 = transaction_session.create(account_id=create_account, amount=13)
    transaction_session.add(transaction1)
    transaction_session.add(transaction2)
    await transaction_session.commit()
    return str(transaction1.id), str(transaction2.id)


@pytest_asyncio.fixture
@patch("redis.asyncio.from_url", return_value=FakeRedis())
async def get_token(mock, app, create_user, dao_session):
    with app.ctx.container.session.override(dao_session):
        request, response = await app.asgi_client.post(
            "/auth", content=json.dumps(pytest.params)
        )
        return response.json["access_token"]


@pytest_asyncio.fixture
@patch("redis.asyncio.from_url", return_value=FakeRedis())
async def get_admin_token(mock, app, create_admin, dao_session):
    with app.ctx.container.session.override(dao_session):
        request, response = await app.asgi_client.post(
            "/auth", content=json.dumps(pytest.admin_params)
        )
        return response.json["access_token"]


@pytest_asyncio.fixture
async def override_container(app, dao_session):
    with app.ctx.container.session.override(dao_session):
        yield
