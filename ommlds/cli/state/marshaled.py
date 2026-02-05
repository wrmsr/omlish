import datetime
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from .storage import StateStorage


T = ta.TypeVar('T')


##


STATE_VERSION = 0


@dc.dataclass(frozen=True)
class MarshaledState:
    version: int

    payload: ta.Any

    created_at: datetime.datetime | None = dc.field(default_factory=lang.utcnow)
    updated_at: datetime.datetime | None = dc.field(default_factory=lang.utcnow)


class MarshaledStateStorage(StateStorage, lang.Abstract):
    def __init__(
            self,
            *,
            version: int = STATE_VERSION,
    ) -> None:
        super().__init__()

        self._version = version

    def _unmarshal_state(self, obj: ta.Any, ty: type[T] | None = None) -> T | None:
        ms = msh.unmarshal(obj, MarshaledState)
        if ms.version < self._version:
            return None
        return msh.unmarshal(ms.payload, ty)

    def _marshal_state(self, obj: ta.Any, ty: type | None = None) -> ta.Any:
        ms = MarshaledState(
            version=self._version,
            payload=msh.marshal(obj, ty),
            updated_at=lang.utcnow(),
        )
        return msh.marshal(ms)
