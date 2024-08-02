import logging
import typing as ta

import sqlalchemy as sa
import sqlalchemy.orm

from omlish import sql

from .users import User
from .users import UserStore


log = logging.getLogger(__name__)


##


Metadata = sa.MetaData()
Base: ta.Any = sa.orm.declarative_base(metadata=Metadata)


class UserModel(
    Base,
):
    __tablename__ = 'users'
    __table_args__ = (
        sa.Index('users_by_email', 'email', unique=True),
    )

    id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)

    email = sa.Column(sa.String(50), nullable=False, unique=True)
    password = sa.Column(sa.String(50), nullable=False)
    name = sa.Column(sa.String(50), nullable=False)


Users = UserModel.__table__


##


class DbUserStore(UserStore):
    def __init__(
            self,
            engine: sql.AsyncEngineLike,
    ) -> None:
        super().__init__()

        self._engine = sql.async_adapt(engine)

    async def setup(self) -> None:
        async with sql.async_adapt(self._engine).connect() as conn:
            async with conn.begin():
                await conn.run_sync(Metadata.create_all)

    async def get_all(self) -> list[User]:
        raise NotImplementedError

    async def get(self, *, id: int | None = None, email: str | None = None) -> User | None:  # noqa
        raise NotImplementedError

    async def create(self, *, email: str, password: str, name: str) -> User:
        raise NotImplementedError

    async def update(self, u: User) -> None:
        raise NotImplementedError
