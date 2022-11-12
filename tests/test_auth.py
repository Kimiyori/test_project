import json
from unittest.mock import patch
from src.db.data_acess_layer.user import UserDAO
from .conftest import *
import pytest


@pytest.mark.usefixtures("dao_session", "override_container")
@patch("redis.asyncio.from_url", return_value=FakeRedis())
async def test_registration_handler(
    mock_redis,
    app,
):
    params = {"username": "testtest", "password": "testtest"}
    _, response = await app.asgi_client.post(
        "/auth/registration", content=json.dumps(params)
    )
    mock_redis.assert_called()
    assert response.status == 201
    assert "link" in response.json


@pytest.mark.usefixtures("dao_session", "override_container")
async def test_registration_handler_without_data(app):
    _, response = await app.asgi_client.post("/auth/registration")
    assert response.status == 400
    assert response.json == {
        "description": "Bad Request",
        "message": "must provide username and password",
        "status": 400,
    }


@pytest.mark.usefixtures("dao_session", "override_container")
async def test_registration_handler_invalid_data(app):
    params = {"username": "test" * 30, "password": "test"}
    _, response = await app.asgi_client.post(
        "/auth/registration", content=json.dumps(params)
    )
    assert response.status == 400
    assert response.json == {
        "description": "Bad Request",
        "message": "name must me in range from 8 to 50",
        "status": 400,
    }


@pytest.mark.usefixtures("override_container")
@patch("redis.asyncio.from_url", return_value=FakeRedis())
async def test_approve_registration(mock_redis, app, dao_session):
    session = UserDAO(dao_session)
    params = {"username": "test"*3, "password": "test"*3}
    _, response = await app.asgi_client.post(
        "/auth/registration", content=json.dumps(params)
    )
    assert response.status == 201
    user = await session.get(id=1)
    status = session.check_status(user)
    assert not status
    link = "/".join(response.json["link"].split("/")[1:])
    print(link)
    _, response = await app.asgi_client.get(link)
    user = await session.get(id=1)
    status = session.check_status(user)
    assert status
    assert response.status == 200
    assert response.json == params


@pytest.mark.usefixtures("create_user", "dao_session", "override_container")
@patch("redis.asyncio.from_url", return_value=FakeRedis())
async def test_auth(mock, app):
    params = {"username": "test", "password": "test"}
    _, response = await app.asgi_client.post("/auth", content=json.dumps(params))
    assert response.status_code == 200
    assert response.json["access_token"]
    assert response.json["refresh_token"]


@pytest.mark.usefixtures("create_user", "dao_session", "override_container")
@patch("redis.asyncio.from_url", return_value=FakeRedis())
async def test_auth_me(mock, app):
    params = {"username": "test", "password": "test"}
    _, response = await app.asgi_client.post("/auth", content=json.dumps(params))
    headers = {"Authorization": f"Bearer {response.json['access_token']}"}
    _, response = await app.asgi_client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json == {"me": {"user_id": 1, "username": "test"}}


@pytest.mark.usefixtures("create_user", "dao_session", "override_container")
@patch("redis.asyncio.from_url", return_value=FakeRedis())
async def test_validate(mock, app):
    params = {"username": "test", "password": "test"}
    _, response = await app.asgi_client.post("/auth", content=json.dumps(params))
    headers = {"Authorization": f"Bearer {response.json['access_token']}"}
    _, response = await app.asgi_client.get("/auth/verify", headers=headers)
    assert response.status_code == 200
    assert response.json == {"valid": True}


@pytest.mark.usefixtures("dao_session", "override_container")
@pytest.mark.usefixtures("create_user")
async def test_auth_invalid_status(app):
    params = {"username": "test", "password": "test"}
    _, response = await app.asgi_client.post(
        "/auth", content=json.dumps({"username": "test"})
    )
    assert response.status_code == 401


@pytest.mark.usefixtures("create_user", "dao_session", "override_container")
@patch("redis.asyncio.from_url", return_value=FakeRedis())
async def test_refresh_token(mock, app):
    params = {"username": "test", "password": "test"}
    _, response = await app.asgi_client.post("/auth", content=json.dumps(params))
    assert response.status_code == 200
    headers = {
        "Authorization": f"Bearer {response.json['access_token']}",
        "content-type": "application/json",
    }
    content = {"refresh_token": response.json["refresh_token"]}
    _, response = await app.asgi_client.post(
        "/auth/refresh", headers=headers, content=json.dumps(content)
    )
    assert response.status_code == 200
    assert response.json["access_token"]
