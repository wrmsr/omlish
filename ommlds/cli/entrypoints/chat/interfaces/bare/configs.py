import typing as ta

from omlish import dataclasses as dc

from ..configs import InterfaceConfig


##


@dc.dataclass(frozen=True, kw_only=True)
class BareInterfaceConfig(InterfaceConfig):
    interactive: bool = False

    use_readline: bool | ta.Literal['auto'] = 'auto'
