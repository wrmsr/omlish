import abc
import typing as ta

from .. import dataclasses as dc
from .. import lang


@dc.dataclass(frozen=True)
class Origin:
    lst: ta.Sequence[str]


@dc.dataclass(frozen=True)
class Origins:
    lst: ta.Sequence[Origin]


class HasOrigins(lang.Abstract):
    @property
    @abc.abstractmethod
    def origins(self) -> Origins | None:
        raise NotImplementedError
