import typing as ta

from omlish import dataclasses as dc


##


@dc.dataclass(frozen=True, kw_only=True)
class StateConfig:
    state: ta.Literal['new', 'continue', 'ephemeral'] = 'continue'
