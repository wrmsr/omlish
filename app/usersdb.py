import abc
import dataclasses as dc
import itertools
import logging

from .users import User
from .users import UserStore
from omlish import check
from omlish import lang


log = logging.getLogger(__name__)


class DbUserStore(UserStore):

    async def get_all(self) -> list[User]:
        pass

    async def get(self, *, id: int | None = None, email: str | None = None) -> User | None:
        pass

    async def create(self, *, email: str, password: str, name: str) -> User:
        pass

    async def update(self, u: User) -> None:
        pass
