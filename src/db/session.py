from typing import Any, AsyncGenerator, Callable
from src.db.base import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.data_acess_layer.abc import DAOType


async def session_factory(
    model: Callable[[AsyncSession], DAOType] | None = None, *args: Any, **kwargs: Any
) -> AsyncGenerator[DAOType, None] | AsyncSession:
    async with Session(*args, **kwargs) as session:
        yield model(session) if model else session
