from pydantic import ValidationError
from dependency_injector.wiring import Provide, inject, Closing
from src.containers import Container
from src.db.data_acess_layer.account import AccountDAO
from src.db.data_acess_layer.transactions import TransactionDAO
from src.exceptions import InvalidUsage
from src.shemas.transactions_shemas import WebHook


def validate_webhook_data(data: dict[str, str | int]) -> WebHook:
    try:
        validated_data = WebHook(**data)
    except ValidationError as error:
        raise InvalidUsage(message=error.errors()[0]["msg"]) from error
    except TypeError as error:
        raise InvalidUsage(message="must provide all fields") from error
    return validated_data


@inject
async def add_amount(
    data: WebHook,
    transaction_session: TransactionDAO = Closing[
        Provide[Container.transaction_session]
    ],
    account_session: AccountDAO = Closing[Provide[Container.account_session]],
) -> int | None:
    transaction = transaction_session.create(
        id=data.transaction_id, account_id=data.account_id, amount=data.amount
    )
    transaction_session.add(transaction)
    new_balance: int | None = await account_session.update_amount(
        account_id=data.account_id, amount=data.amount
    )
    await account_session.commit()
    return new_balance
