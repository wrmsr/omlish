import typing as ta

from omlish import dataclasses as dc
from omlish import lang


with lang.auto_proxy_import(globals()):
    from ...content import content as _content


##


@dc.dataclass(frozen=True, kw_only=True)
class UserConfig:
    initial_system_content: ta.Optional['_content.Content'] = None
    initial_user_content: ta.Optional['_content.Content'] = None
