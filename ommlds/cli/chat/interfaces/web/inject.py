from omlish import inject as inj
from omlish import lang

from ...configs import ChatConfig
from ..base import ChatInterface
from .configs import WebInterfaceConfig
from .types import ServerPort


with lang.auto_proxy_import(globals()):
    from . import interface as _interface


##


def bind_web(
        cfg: WebInterfaceConfig = WebInterfaceConfig(),
        *,
        chat_cfg: ChatConfig = ChatConfig(),
) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.bind(_interface.WebChatInterface, singleton=True),
        inj.bind(ChatInterface, to_key=_interface.WebChatInterface),

        inj.bind(ServerPort, to_const=cfg.port),
    ])

    #

    return inj.as_elements(*els)
