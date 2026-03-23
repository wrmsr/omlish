from omlish import inject as inj
from omlish import lang

from .bare.configs import BareInterfaceConfig
from .configs import InterfaceConfig
from .textual.configs import TextualInterfaceConfig


with lang.auto_proxy_import(globals()):
    from .bare import inject as _bare
    from .textual import inject as _textual


##


def bind_interface(cfg: InterfaceConfig = BareInterfaceConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    if isinstance(cfg, TextualInterfaceConfig):
        els.append(_textual.bind_textual(cfg))

    elif isinstance(cfg, BareInterfaceConfig):
        els.append(_bare.bind_bare(cfg))

    else:
        raise TypeError(cfg)

    return inj.as_elements(*els)
