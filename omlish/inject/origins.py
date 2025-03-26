import abc
import typing as ta

from .. import dataclasses as dc
from .. import lang


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Origin:
    lst: ta.Sequence[str]


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Origins:
    lst: ta.Sequence[Origin]

    def __iter__(self) -> ta.Iterator[Origin]:
        yield from self.lst


class HasOrigins(lang.Abstract):
    @property
    @abc.abstractmethod
    def origins(self) -> Origins:
        raise NotImplementedError
