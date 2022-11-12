from src.db.data_acess_layer.goods import GoodsDAO
from .conftest import *
import pytest


@pytest_asyncio.fixture
async def create_goods(dao_session, faker):
    session = GoodsDAO(dao_session)
    for _ in range(10):
        instance = session.create(
            name=faker.pystr(),
            description=faker.text(max_nb_chars=500),
            price=faker.pyint(),
        )
        session.add(instance)
    await session.commit()


@pytest.mark.usefixtures("dao_session", "override_container")
async def test_goods_list_unauth(app):
    _, response = await app.asgi_client.get("/goods")
    assert response.status_code == 400


@pytest.mark.usefixtures("create_goods", "dao_session", "override_container")
async def test_goods_list_auth(app, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    _, response = await app.asgi_client.get("/goods", headers=headers)
    assert response.status_code == 200
    assert len(response.json["goods"]) == 10


@pytest.mark.usefixtures("create_goods", "dao_session", "override_container")
@pytest.mark.parametrize("balance", [0])
async def test_sale_good_not_enough_money(app, get_token, create_account):
    headers = {"Authorization": f"Bearer {get_token}"}
    content = {"account_id": create_account}
    _, response = await app.asgi_client.post(
        "/goods/buy/1", headers=headers, content=json.dumps(content)
    )
    assert response.status_code == 402


@pytest.mark.usefixtures("create_goods", "dao_session", "override_container")
@pytest.mark.parametrize("balance", [11111111])
async def test_sale_good(app, get_token, create_account):
    headers = {"Authorization": f"Bearer {get_token}"}
    content = {"account_id": create_account}
    _, response = await app.asgi_client.post(
        "/goods/buy/1", headers=headers, content=json.dumps(content)
    )
    assert response.status_code == 200
    assert response.json == {"msg": "successful"}


@pytest.mark.usefixtures("dao_session", "override_container")
async def test_create_good_invalid_data(app, get_admin_token):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    content = {"name": "test", "description": "test"}
    _, response = await app.asgi_client.post(
        "/admin/goods/create", headers=headers, content=json.dumps(content)
    )
    assert response.status_code == 400


@pytest.mark.usefixtures("dao_session", "override_container")
async def test_create_good(app, get_admin_token):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    content = {"name": "test", "description": "test", "price": 123}
    _, response = await app.asgi_client.post(
        "/admin/goods/create", headers=headers, content=json.dumps(content)
    )
    assert response.status_code == 201
    assert response.json == {"message": "good successfuly created", "good_id": 1}

@pytest.mark.usefixtures("override_container", "create_goods")
async def test_update_good_not_valid_data(app, dao_session, get_admin_token):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    content = {}
    _, response = await app.asgi_client.put(
        "/admin/goods/update/1", headers=headers, content=json.dumps(content)
    )
    assert response.status_code == 400


@pytest.mark.usefixtures("override_container", "create_goods")
async def test_update_good(app, dao_session, get_admin_token):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    content = {"name": "test"}
    goods_session = GoodsDAO(dao_session)
    good = await goods_session.get(id=1)
    assert good.name != "test"
    _, response = await app.asgi_client.put(
        "/admin/goods/update/1", headers=headers, content=json.dumps(content)
    )
    assert response.status_code == 204
    assert response.json == ''
    good = await goods_session.get(id=1)
    assert good.name == "test"

@pytest.mark.usefixtures("override_container", "create_goods")
async def test_update_good(app, dao_session, get_admin_token):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    content = {"name": "test"}
    goods_session = GoodsDAO(dao_session)
    good = await goods_session.get(id=1)
    assert good.name != "test"
    _, response = await app.asgi_client.put(
        "/admin/goods/update/1", headers=headers, content=json.dumps(content)
    )
    assert response.status_code == 204
    assert response.json == ''
    good = await goods_session.get(id=1)
    assert good.name == "test"

@pytest.mark.usefixtures("override_container", "create_goods")
async def test_delete_good(app, dao_session, get_admin_token):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    goods_session = GoodsDAO(dao_session)
    good = await goods_session.get(id=1)
    assert good
    _, response = await app.asgi_client.delete(
        "/admin/goods/delete/1", headers=headers
    )
    assert response.status_code == 204
    assert response.json == ''
    good = await goods_session.get(id=1)
    assert not good

@pytest.mark.usefixtures("dao_session","override_container", "create_goods")
async def test_delete_good_fail(app, get_admin_token):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    _, response = await app.asgi_client.delete(
        "/admin/goods/delete/111", headers=headers
    )
    assert response.status_code == 204
