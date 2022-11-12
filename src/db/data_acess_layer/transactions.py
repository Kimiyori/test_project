from typing import Any
from sqlalchemy import select
from src.db.data_acess_layer.abc import AbstractDAO
from src.db.models import Transaction


class TransactionDAO(AbstractDAO):
    """Data Acess Layer for author table"""

    model = Transaction

    async def get(self, **kwargs: Any) -> Transaction | None:
        query = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(query)
        tpl: Transaction | None = result.scalar()
        return tpl

    async def get_all(self) -> list[Transaction]:
        query = select(self.model)
        result = await self.session.execute(query)
        lst = result.scalars().all()
        return lst

    async def get_all_user_transactions(self, **kwargs: Any) -> list[Transaction]:
        query = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(query)
        return result.scalars().all()
