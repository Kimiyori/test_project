from abc import ABC
from typing import Any, ClassVar, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import TableType

DAOType = TypeVar("DAOType", bound="AbstractDAO")  # pylint: disable =invalid-name


class AbstractDAO(ABC):
    """Abstract base class for Data Access Layer"""

    model: ClassVar[TableType] = NotImplemented

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def add(self, item: TableType) -> None:
        self.session.add(item)

    def add_all(self, items: list[TableType]) -> None:
        self.session.add_all(items)

    def create(self, **kwargs: Any) -> Any:
        instance = self.model(**kwargs)
        return instance

    async def commit(self) -> None:
        await self.session.commit()
