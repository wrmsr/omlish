from omlish import dataclasses as dc
from omlish import lang


with lang.auto_proxy_import(globals()):
    from ...content import content as _content


##


@dc.dataclass(frozen=True, kw_only=True)
class UserConfig:
    initial_system_content: _content.Content | None = None
    initial_user_content: _content.Content | None = None
