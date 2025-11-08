import typing as ta

from omlish import dataclasses as dc

from ...... import minichain as mc


##


@dc.dataclass(frozen=True, kw_only=True)
class UserConfig:
    initial_system_content: ta.Optional['mc.Content'] = None
    initial_user_content: ta.Optional['mc.Content'] = None

    interactive: bool = False
    use_readline: bool | ta.Literal['auto'] = 'auto'
