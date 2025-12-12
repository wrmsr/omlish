from omlish import inject as inj
from omlish import lang

from ..base import ChatInterface
from ..configs import InterfaceConfig
from .interface import BareChatInterface


with lang.auto_proxy_import(globals()):
    from .....inputs import asyncs as _inputs_asyncs
    from .....inputs import sync as _inputs_sync


##


def bind_bare(cfg: InterfaceConfig = InterfaceConfig()) -> inj.Elements:
    els: list[inj.Elemental] = [
        inj.bind(ChatInterface, to_ctor=BareChatInterface, singleton=True),
    ]

    if cfg.interactive:
        els.extend([
            inj.bind(_inputs_sync.SyncStringInput, to_const=_inputs_sync.InputSyncStringInput(use_readline=cfg.use_readline)),  # noqa
            inj.bind(_inputs_asyncs.AsyncStringInput, to_ctor=_inputs_asyncs.ThreadAsyncStringInput, singleton=True),
        ])

    return inj.as_elements(*els)
