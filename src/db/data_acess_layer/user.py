from typing import Any
from sqlalchemy import func, select, update
from sqlalchemy.engine.row import Row
from src.db.data_acess_layer.abc import AbstractDAO
from src.db.models import Account, UserStatus, UserTable


class UserDAO(AbstractDAO):
    """Data Acess Layer for author table"""

    model = UserTable

    async def get(self, **kwargs: Any) -> UserTable | None:
        query = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(query)
        tpl: UserTable | None = result.scalar()
        return tpl

    async def get_all_with_accounts(self) -> list[Row]:
        query = (
            select(
                self.model.id,
                self.model.username,
                self.model.type,
                self.model.status,
                func.json_agg(func.json_build_array(Account.id, Account.balance)).label(
                    "accounts_list"
                ),
            )
            .join(Account, isouter=True)
            .group_by(self.model.id)
            .order_by(self.model.id)
        )

        result = await self.session.execute(query)
        lst = result.all()
        return lst

    async def conf_new_user(self, id: int) -> Row | None:
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(status=UserStatus.ACTIVE)
            .returning(self.model.username, self.model.password)
        )
        res = await self.session.execute(query)
        fetch = res.first()
        return fetch

    def check_status(self, user: UserTable) -> bool:
        return user.status == UserStatus.ACTIVE
