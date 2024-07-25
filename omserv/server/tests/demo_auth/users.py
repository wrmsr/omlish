import dataclasses as dc
import itertools
import logging

from omlish import check


log = logging.getLogger(__name__)


@dc.dataclass(frozen=True)
class User:
    id: int
    email: str
    password: str
    name: str


class Users:
    def __init__(self) -> None:
        super().__init__()
        self._next_user_id = itertools.count()
        self._users_by_id: dict[int, User] = {}
        self._user_ids_by_email: dict[str, int] = {}

    def create(
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

    def update(self, u: User) -> None:
        e = self._users_by_id[u.id]
        check.equal(u.email, e.email)
        self._users_by_id[u.id] = u


USERS = Users()
