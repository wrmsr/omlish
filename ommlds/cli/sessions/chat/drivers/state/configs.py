import typing as ta

from omlish import dataclasses as dc

from ...... import minichain as mc


##


@dc.dataclass(frozen=True, kw_only=True)
class StateConfig(mc.drivers.StateConfig):
    state: ta.Literal['new', 'continue', 'ephemeral'] = 'continue'

    chat_id: str | None = None
