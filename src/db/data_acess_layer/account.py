from typing import Any
from sqlalchemy import select, update
from src.db.data_acess_layer.abc import AbstractDAO
from src.db.models import Account


class AccountDAO(AbstractDAO):
    """Data Acess Layer for author table"""

    model = Account

    async def get(self, **kwargs: Any) -> Account | None:
        query = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(query)
        tpl: Account | None = result.scalar()
        return tpl

    async def get_all_user_accounts(self, **kwargs: Any) -> list[Account]:
        query = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_amount(self, account_id: str, amount: int) -> int | None:
        query = (
            update(self.model)
            .where(self.model.id == account_id)
            .values(balance=self.model.balance + amount)
            .returning(self.model.balance)
        )
        res = await self.session.execute(query)
        fetch = res.first()
        balance: int = fetch[0] if fetch else None
        return balance

    async def subtract_from_balance(self, account_id: str, price: int) -> None:
        query = (
            update(self.model)
            .where(self.model.id == account_id)
            .values(balance=self.model.balance - price)
        )
        await self.session.execute(query)
