import uuid

from src.db.data_acess_layer.transactions import TransactionDAO
from .conftest import *
import pytest
from Crypto.Hash import SHA1
from src.config import SECRET
import json


@pytest.mark.parametrize("balance", [123])
@pytest.mark.usefixtures("override_container")
async def test_account_replenishment(app, dao_session, get_token, create_account):
    headers = {"Authorization": f"Bearer {get_token}"}
    transaction_id = str(uuid.uuid4())
    code = f"{SECRET}:{transaction_id}:{1}:{create_account}:{100}"
    signature = SHA1.new()
    signature.update(code.encode())
    content = {
        "signature": signature.hexdigest(),
        "transaction_id": transaction_id,
        "user_id": 1,
        "account_id": create_account,
        "amount": 100,
    }
    _, response = await app.asgi_client.post(
        "/payment/webhook", headers=headers, content=json.dumps(content)
    )
    assert response.status_code == 200
    assert response.json == {
        "msg": "money has been successfully credited to the account",
        "new_balance": 223,
    }
    transaction_session = TransactionDAO(dao_session)
    transaction = await transaction_session.get(id=transaction_id)
    assert transaction
    account_session = AccountDAO(dao_session)
    account = await account_session.get(id=create_account)
    assert account.balance == 223
