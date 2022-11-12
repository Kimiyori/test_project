from dependency_injector.wiring import Provide, inject, Closing
from src.containers import Container
from src.db.data_acess_layer.account import AccountDAO
from src.db.data_acess_layer.transactions import TransactionDAO
from src.db.data_acess_layer.user import UserDAO
from src.db.models import UserStatus, UserTable, UserType
from src.exceptions import NotFoundInstance


@inject
async def get_user(
    user_id: int,
    user_session: UserDAO = Closing[Provide[Container.user_session]],
) -> UserTable | None:
    user = await user_session.get(id=user_id)
    return user


@inject
async def get_user_accounts(
    user_id: int,
    account_session: AccountDAO = Closing[Provide[Container.account_session]],
) -> dict[str, list[dict[str, str | int | None]]]:
    accounts = await account_session.get_all_user_accounts(user_id=user_id)
    dct = {
        "accounts": [
            {
                "id": str(account.id),
                "balance": account.balance,
            }
            for account in accounts
        ]
    }
    return dct


@inject
async def get_user_transactions(
    user_id: int,
    transaction_session: TransactionDAO = Closing[
        Provide[Container.transaction_session]
    ],
    account_session: AccountDAO = Closing[Provide[Container.account_session]],
) -> dict[str, list[dict[str, str | int | None]]]:
    accounts = await account_session.get_all_user_accounts(user_id=user_id)
    transactions = []
    for account in accounts:
        transaction = await transaction_session.get_all_user_transactions(
            account_id=account.id
        )
        transactions.append(transaction)
    dct = {
        "transactions": [
            {
                "id": str(transaction.id),
                "amount": transaction.amount,
            }
            for transaction in transactions[0]
        ]
    }

    return dct


@inject
async def validate_admin(
    user_id: int, user_session: UserDAO = Closing[Provide[Container.user_session]]
) -> bool:
    user = await user_session.get(id=user_id)
    if not user:
        raise NotFoundInstance
    res: bool = user.type == UserType.ADMIN
    return res


@inject
async def get_users(
    user_session: UserDAO = Closing[Provide[Container.user_session]],
) -> dict[str, list[dict[str, int | str | list[dict[str, str | int]]]]]:
    users = await user_session.get_all_with_accounts()
    dct = {
        "users": [
            {
                "user_id": user.id,
                "username": user.username,
                "user_type": user.type.name if user.type else None,
                "user_status": user.status.name if user.status else None,
                "accounts": [
                    {"account_id": account[0], "account_balance": account[1]}
                    for account in user.accounts_list
                    if account[0] is not None
                ],
            }
            for user in users
        ]
    }
    return dct


@inject
async def set_user_status(
    status: str,
    user: UserTable,
    user_session: UserDAO = Closing[Provide[Container.user_session]],
) -> str:
    if status == "disable":
        new_status = UserStatus.INACTIVE
    elif status == "enable":
        new_status = UserStatus.ACTIVE
    if user.status == new_status:
        return "the user already had this status"
    user.status = UserStatus.INACTIVE
    await user_session.commit()
    return f"successfully {status} user account"
