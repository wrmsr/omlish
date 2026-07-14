import datetime
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..metadata import CreatedAt
from .general import GeneralTransform


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class CreatedAtAddingGeneralTransform(GeneralTransform[T]):
    clock: ta.Callable[[], datetime.datetime] = dc.field(default=lang.utcnow)

    def transform(self, o: T) -> ta.Sequence[T]:
        if CreatedAt not in o.metadata:  # type: ignore[attr-defined]
            o = o.with_metadata(CreatedAt(self.clock()))  # type: ignore[attr-defined]
        return [o]
