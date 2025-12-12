from omlish import inject as inj
from omlish import lang

from .configs import InterfaceConfig

with lang.auto_proxy_import(globals()):
    from .textual import inject as _textual


##


def bind_interface(cfg: InterfaceConfig = InterfaceConfig()) -> inj.Elements:
    _textual.bind_textual()
    raise NotImplementedError
