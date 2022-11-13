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
    _, response = await app.asgi_client.post(
        "/auth/register", content=json.dumps(pytest.params)
    )
    mock_redis.assert_called()
    assert response.status == 201
    assert "link" in response.json


@pytest.mark.usefixtures("dao_session", "override_container")
async def test_registration_handler_without_data(app):
    _, response = await app.asgi_client.post("/auth/register")
    assert response.status == 400
    assert response.json == {
        "description": "Bad Request",
        "message": "must provide username and password",
        "status": 400,
    }


@pytest.mark.usefixtures("dao_session", "override_container")
async def test_registration_handler_invalid_data(app):
    params = {"username": "test" * 3, "password": "test"}
    _, response = await app.asgi_client.post(
        "/auth/register", content=json.dumps(params)
    )
    assert response.status == 400
    assert response.json == {
        "description": "Bad Request",
        "message": "ensure this value has at least 8 characters",
        "status": 400,
    }


@pytest.mark.usefixtures("override_container")
@patch("redis.asyncio.from_url", return_value=FakeRedis())
async def test_approve_registration(mock_redis, app, dao_session):
    session = UserDAO(dao_session)
    _, response = await app.asgi_client.post(
        "/auth/register", content=json.dumps(pytest.params)
    )
    assert response.status == 201
    user = await session.get(id=1)
    status = session.check_status(user)
    assert not status
    link = "/".join(response.json["link"].split("/")[1:])
    _, response = await app.asgi_client.put(link)
    assert response.status == 200
    assert response.json["access_token"]
    assert response.json["refresh_token"]
    user = await session.get(id=1)
    status = session.check_status(user)
    assert status

@pytest.mark.usefixtures("create_user", "dao_session", "override_container")
@patch("redis.asyncio.from_url", return_value=FakeRedis())
async def test_auth(mock, app):
    _, response = await app.asgi_client.post("/auth", content=json.dumps(pytest.params))
    assert response.status_code == 200
    assert response.json["access_token"]
    assert response.json["refresh_token"]


@pytest.mark.usefixtures("create_user", "dao_session", "override_container")
@patch("redis.asyncio.from_url", return_value=FakeRedis())
async def test_auth_me(mock, app):
    _, response = await app.asgi_client.post("/auth", content=json.dumps(pytest.params))
    headers = {"Authorization": f"Bearer {response.json['access_token']}"}
    _, response = await app.asgi_client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json == {"me": {"user_id": 1, "username": "test_just_user"}}


@pytest.mark.usefixtures("create_user", "dao_session", "override_container")
@patch("redis.asyncio.from_url", return_value=FakeRedis())
async def test_validate(mock, app):
    _, response = await app.asgi_client.post("/auth", content=json.dumps(pytest.params))
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
    _, response = await app.asgi_client.post("/auth", content=json.dumps(pytest.params))
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
