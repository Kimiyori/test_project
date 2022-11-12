from typing import Any
from sqlalchemy import select, update, delete
from src.db.data_acess_layer.abc import AbstractDAO
from src.db.models import Commodity


class GoodsDAO(AbstractDAO):
    """Data Acess Layer for author table"""

    model = Commodity

    async def get(self, **kwargs: Any) -> Commodity | None:
        query = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(query)
        tpl: Commodity | None = result.scalar()
        return tpl

    async def get_all(self) -> list[Commodity]:
        query = select(self.model)
        result = await self.session.execute(query)
        lst = result.scalars().all()
        return lst

    async def update(self, good_id: int, **kwargs: str | int) -> None:
        query = update(self.model).where(self.model.id == good_id).values(**kwargs)
        await self.session.execute(query)

    async def delete(self, good_id: int) -> None:
        query = delete(self.model).where(self.model.id == good_id)
        await self.session.execute(query)
