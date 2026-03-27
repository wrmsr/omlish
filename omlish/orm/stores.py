import abc
import typing as ta

from .. import dataclasses as dc
from .. import lang
from .mappers import Mapper
from .snaps import Snap


##


class Store(lang.Abstract):
    @abc.abstractmethod
    def fetch(self, m: Mapper, k: ta.Any) -> Snap | None:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def lookup(self, m: Mapper, where: ta.Mapping[str, ta.Any]) -> ta.Sequence[Snap]:
        raise NotImplementedError

    #

    @ta.final
    @dc.dataclass(frozen=True, kw_only=True)
    class FlushBatch:
        insert: ta.Sequence[Snap] | None = None
        update: ta.Sequence[tuple[ta.Any, Snap]] | None = None
        delete: ta.Sequence[ta.Any] | None = None  # noqa

    @ta.final
    @dc.dataclass(frozen=True, kw_only=True)
    class FlushResult:
        inserted_auto_keys: ta.Mapping[ta.Any, ta.Any] | None = None

    @abc.abstractmethod
    def flush(self, m: Mapper, b: FlushBatch) -> FlushResult:
        raise NotImplementedError
