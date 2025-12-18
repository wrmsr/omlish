from omlish import inject as inj
from omlish import lang

from .configs import InterfaceConfig


with lang.auto_proxy_import(globals()):
    from .bare import inject as _bare
    from .textual import inject as _textual


##


def bind_interface(cfg: InterfaceConfig = InterfaceConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    if cfg.use_textual:
        els.append(_textual.bind_textual(cfg))

    else:
        els.append(_bare.bind_bare(cfg))

    return inj.as_elements(*els)
