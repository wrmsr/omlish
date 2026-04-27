import typing as ta
import uuid

from omlish import dataclasses as dc

from ...... import minichain as mc


##


@dc.dataclass(frozen=True, kw_only=True)
class StateConfig(mc.drivers.StateConfig):
    state: ta.Literal['new', 'continue'] = 'continue'

    chat_id: uuid.UUID | None = None
