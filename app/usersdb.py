import logging
import typing as ta

import sqlalchemy as sa
import sqlalchemy.orm

from omlish import check
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
            engine: sql.AsyncEngine,
    ) -> None:
        super().__init__()

        self._engine = engine
        self._has_setup = False

    async def _setup(self) -> None:
        if not self._has_setup:
            async with sql.async_adapt(self._engine).connect() as conn:
                async with conn.begin():
                    await conn.run_sync(Metadata.create_all)
            self._has_setup = True

    async def get_all(self) -> list[User]:
        await self._setup()

        conn: sql.AsyncConnection
        async with self._engine.connect() as conn:
            rows = (await conn.execute(sa.select(Users))).fetchall()

        raise NotImplementedError

    async def get(self, *, id: int | None = None, email: str | None = None) -> User | None:  # noqa
        await self._setup()

        conn: sql.AsyncConnection
        async with self._engine.connect() as conn:
            if id is not None:
                rows = (await conn.execute(sa.select(Users).where(Users.c.id == id))).fetchall()
            elif email is not None:
                rows = (await conn.execute(sa.select(Users).where(Users.c.email == email))).fetchall()
            else:
                raise TypeError('Must specify a filter')

        if not rows:
            return None

        row = check.single(rows)
        return User(
            id=row.id,
            email=row.email,
            password=row.email,
            name=row.name,
        )

    async def create(self, *, email: str, password: str, name: str) -> User:
        await self._setup()
        raise NotImplementedError

    async def update(self, u: User) -> None:
        await self._setup()
        raise NotImplementedError
