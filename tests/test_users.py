from .conftest import *
import pytest
from src.db.models import UserStatus


@pytest.mark.parametrize("balance", [123])
@pytest.mark.usefixtures("dao_session", "override_container")
async def test_user_accounts(app, get_token, create_account):
    headers = {"Authorization": f"Bearer {get_token}"}
    _, response = await app.asgi_client.get("/user/accounts", headers=headers)
    assert response.status_code == 200
    assert response.json == {"accounts": [{"id": create_account, "balance": 123}]}


@pytest.mark.parametrize("balance", [123])
@pytest.mark.usefixtures("dao_session", "override_container")
async def test_user_transactions(app, get_token, create_transactions):
    headers = {"Authorization": f"Bearer {get_token}"}
    _, response = await app.asgi_client.get("/user/transactions", headers=headers)
    assert response.status_code == 200
    assert response.json == {
        "transactions": [
            {"amount": 11, "id": create_transactions[0]},
            {"amount": 13, "id": create_transactions[1]},
        ]
    }


@pytest.mark.parametrize("balance", [123])
@pytest.mark.usefixtures("dao_session", "override_container")
async def test_get_users_not_admin(app, get_token, create_account):
    headers = {"Authorization": f"Bearer {get_token}"}
    _, response = await app.asgi_client.get("/admin/users", headers=headers)
    assert response.status_code == 403


@pytest.mark.parametrize("balance", [123])
@pytest.mark.usefixtures("dao_session", "override_container")
async def test_get_users(app, get_admin_token, create_account):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    _, response = await app.asgi_client.get("/admin/users", headers=headers)
    assert response.status_code == 200
    assert response.json == {
        "users": [
            {
                "user_id": 1,
                "username": pytest.admin_params["username"],
                "user_type": "ADMIN",
                "user_status": "ACTIVE",
                "accounts": [],
            },
            {
                "user_id": 2,
                "username": pytest.params["username"],
                "user_type": "REGULAR_USER",
                "user_status": "ACTIVE",
                "accounts": [
                    {
                        "account_id": create_account,
                        "account_balance": 123,
                    }
                ],
            },
        ]
    }


@pytest.mark.parametrize("balance", [123])
@pytest.mark.usefixtures("override_container", "create_account")
async def test_disable_user(app, dao_session, get_admin_token):
    user_session = UserDAO(dao_session)
    user = await user_session.get(id=2)
    assert user.status == UserStatus.ACTIVE
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    _, response = await app.asgi_client.get(
        "/admin/change_user_status/disable/2", headers=headers
    )
    assert response.status_code == 200
    assert response.json == {"message": "successfully disable user account"}
    user = await user_session.get(id=2)
    assert user.status == UserStatus.INACTIVE


@pytest.mark.parametrize("balance", [123])
@pytest.mark.usefixtures("override_container", "create_account")
async def test_disable_user_already_disabled(app, dao_session, get_admin_token):
    user_session = UserDAO(dao_session)
    user = await user_session.get(id=2)
    user.status = UserStatus.INACTIVE
    await user_session.commit()
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    _, response = await app.asgi_client.get(
        "/admin/change_user_status/disable/2", headers=headers
    )
    assert response.status_code == 200
    assert response.json == {"message": "the user already had this status"}
