import typing as ta

from omlish import dataclasses as dc


##


@dc.dataclass(frozen=True, kw_only=True)
class InterfaceConfig:
    interactive: bool = False
    use_readline: bool | ta.Literal['auto'] = 'auto'
