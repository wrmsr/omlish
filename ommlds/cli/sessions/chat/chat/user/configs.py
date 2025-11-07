import typing as ta

from omlish import dataclasses as dc


##


@dc.dataclass(frozen=True)
class UserInputConfig:
    interactive: bool = False
    use_readline: bool | ta.Literal['auto'] = 'auto'
