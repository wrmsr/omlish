from omlish import inject as inj
from omlish import lang

from ..configs import ChatConfig
from .bare.configs import BareInterfaceConfig
from .configs import InterfaceConfig
from .textual.configs import TextualInterfaceConfig
from .web.configs import WebInterfaceConfig


with lang.auto_proxy_import(globals()):
    from .bare import inject as _bare
    from .textual import inject as _textual
    from .web import inject as _web


##


def bind_interface(
        cfg: InterfaceConfig = BareInterfaceConfig(),
        *,
        chat_cfg: ChatConfig = ChatConfig(),
) -> inj.Elements:
    els: list[inj.Elemental] = []

    if isinstance(cfg, TextualInterfaceConfig):
        els.append(_textual.bind_textual(cfg, chat_cfg=chat_cfg))

    elif isinstance(cfg, BareInterfaceConfig):
        els.append(_bare.bind_bare(cfg, chat_cfg=chat_cfg))

    elif isinstance(cfg, WebInterfaceConfig):
        els.append(_web.bind_web(cfg, chat_cfg=chat_cfg))

    else:
        raise TypeError(cfg)

    return inj.as_elements(*els)
