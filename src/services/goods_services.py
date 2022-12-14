from dependency_injector.wiring import Provide, inject, Closing
from src.containers import Container
from src.db.data_acess_layer.account import AccountDAO
from src.db.data_acess_layer.goods import GoodsDAO
from src.exceptions import NotFoundInstance, PaymentError
from src.shemas.goods_shemas import CommodityCreate, CommodityUpdate


@inject
async def get_goods(
    goods_session: GoodsDAO = Closing[Provide[Container.goods_session]],
) -> dict[str, list[dict[str, str | int | None]]]:
    """service for getting all goods from db

    Returns:
        dict[str, list[dict[str, str | int | None]]]: dict with following shema:
            {
        "goods": [
                    {
                        "id": good.id,
                        "name": good.name,
                        "description": good.description,
                        "price": good.price,
                    },
                    ...
                ]
            }
    """
    goods = await goods_session.get_all()
    dct = {
        "goods": [
            {
                "id": good.id,
                "name": good.name,
                "description": good.description,
                "price": good.price,
            }
            for good in goods
        ]
    }
    return dct


@inject
async def handle_sale(
    account_id: str,
    user_id: int,
    good_id: int,
    goods_session: GoodsDAO = Closing[Provide[Container.goods_session]],
    account_session: AccountDAO = Closing[Provide[Container.account_session]],
) -> None:
    """commit sale and subtract money from user account
    Args:
        account_id (str)
        user_id (int)
        good_id (int)

    Raises:
        NotFoundInstance:throw if not found good or account
        PaymentError: if on account not enough money
    """
    good = await goods_session.get(id=good_id)
    if good is None:
        raise NotFoundInstance
    account = await account_session.get(id=account_id, user_id=user_id)
    if account is None:
        raise NotFoundInstance
    if good.price and account.balance is not None and account.balance < good.price:
        raise PaymentError
    assert good.price is not None
    await account_session.subtract_from_balance(account_id, good.price)
    await account_session.commit()


@inject
async def create_good_instance(
    good: CommodityCreate,
    goods_session: GoodsDAO = Closing[Provide[Container.goods_session]],
) -> int:
    """service for creating good

    Args:
        good (CommodityCreate):instance sheme

    Returns:
        int: id good that was created
    """
    created = goods_session.create(
        name=good.name, description=good.description, price=good.price
    )
    goods_session.add(created)
    await goods_session.commit()
    created_id: int = created.id
    return created_id


@inject
async def update_good_instance(
    good_id: int,
    good: CommodityUpdate,
    goods_session: GoodsDAO = Closing[Provide[Container.goods_session]],
) -> None:
    """service for update good

    Args:
        good_id (int): good id
        good (CommodityUpdate): indo that need to be updated
    """
    await goods_session.update(good_id, **good.dict(exclude_none=True))


@inject
async def delete_good_instance(
    good_id: int,
    goods_session: GoodsDAO = Closing[Provide[Container.goods_session]],
) -> None:
    """service for delete good

    Args:
        good_id (int): good id
    """
    await goods_session.delete(good_id)
