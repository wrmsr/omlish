import dataclasses as dc
import typing as ta

from .errors import MalformedNuhError


##


@dc.dataclass(frozen=True)
class Nuh:
    name: str | None = None
    user: str | None = None
    host: str | None = None

    @property
    def tuple(self) -> tuple[str | None, ...]:
        return (self.name, self.user, self.host)

    def __iter__(self) -> ta.Iterator[str | None]:
        return iter(self.tuple)

    @classmethod
    def parse(cls, inp: str) -> 'Nuh':
        if not inp:
            raise MalformedNuhError

        host: str | None = None
        host_start = inp.find('@')
        if host_start != -1:
            host = inp[host_start + 1:]
            inp = inp[:host_start]

        user_start = inp.find('!')
        user: str | None = None
        if user_start != -1:
            user = inp[user_start + 1:]
            inp = inp[:user_start]

        return cls(
            name=inp or None,
            user=user,
            host=host,
        )

    @property
    def canonical(self) -> str:
        parts = []
        if (n := self.name) is not None:
            parts.append(n)
        if (u := self.user) is not None:
            parts.append(f'!{u}')
        if (h := self.host) is not None:
            parts.append(f'@{h}')
        return ''.join(parts)
