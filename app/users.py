import abc
import dataclasses as dc
import itertools
import logging

from omlish import check
from omlish import lang


log = logging.getLogger(__name__)


##


@dc.dataclass(frozen=True)
class User:
    id: int
    email: str
    password: str
    name: str

    auth_token: str | None = None


##


class UserStore(lang.Abstract):
    @abc.abstractmethod
    async def get_all(self) -> list[User]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(
            self,
            *,
            id: int | None = None,  # noqa
            email: str | None = None,
    ) -> User | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def create(
            self,
            *,
            email: str,
            password: str,
            name: str,
    ) -> User:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, u: User) -> None:
        raise NotImplementedError


##


class InMemoryUserStore(UserStore):
    def __init__(self) -> None:
        super().__init__()

        self._next_user_id = itertools.count()
        next(self._next_user_id)

        self._users_by_id: dict[int, User] = {}
        self._user_ids_by_email: dict[str, int] = {}

    async def get_all(self) -> list[User]:
        return list(self._users_by_id.values())

    async def get(
            self,
            *,
            id: int | None = None,  # noqa
            email: str | None = None,
    ) -> User | None:
        if id is not None:
            return self._users_by_id.get(id)
        elif email is not None:
            i = self._user_ids_by_email.get(email)
            return self._users_by_id[i] if i is not None else None
        else:
            return None

    async def create(
            self,
            *,
            email: str,
            password: str,
            name: str,
    ) -> User:
        check.not_in(email, self._user_ids_by_email)
        u = User(
            id=next(self._next_user_id),
            email=email,
            password=password,
            name=name,
        )
        self._users_by_id[u.id] = u
        self._user_ids_by_email[u.email] = u.id
        return u

    async def update(self, u: User) -> None:
        e = self._users_by_id[u.id]
        check.equal(u.email, e.email)
        self._users_by_id[u.id] = u
