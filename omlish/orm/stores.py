import abc
import typing as ta

from .. import lang
from .mappers import Mapper
from .snaps import Snap


##


class Store(lang.Abstract):
    @abc.abstractmethod
    def fetch(self, m: Mapper, k: ta.Any) -> Snap | None:
        raise NotImplementedError

    @abc.abstractmethod
    def lookup(self, m: Mapper, where: ta.Mapping[str, ta.Any]) -> ta.Sequence[Snap]:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def insert(self, m: Mapper, snaps: ta.Sequence[Snap]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def auto_key_insert(self, m: Mapper, snaps: ta.Sequence[Snap]) -> ta.Mapping[ta.Any, ta.Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, m: Mapper, diffs: ta.Sequence[tuple[ta.Any, Snap]]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, m: Mapper, keys: ta.Sequence[ta.Any]) -> None:
        raise NotImplementedError
