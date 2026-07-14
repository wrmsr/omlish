from omlish import inject as inj
from omlish import lang

from ..types import Entrypoint
from .configs import ChatConfig


with lang.auto_proxy_import(globals()):
    from . import entrypoint as _entrypoint
    from .interfaces import inject as _interfaces


##


def bind_chat(cfg: ChatConfig = ChatConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        _interfaces.bind_interface(cfg.interface, chat_cfg=cfg),
    ])

    #

    els.extend([
        inj.bind(Entrypoint, to_ctor=_entrypoint.ChatEntrypoint, singleton=True),
    ])

    #

    return inj.as_elements(*els)
