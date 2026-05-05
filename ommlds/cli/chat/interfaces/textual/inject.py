# ruff: noqa: SLF001
"""
FIXME:
 - too lazy to lazy import guts like every other proper inject module lol >_<
"""
import contextlib
import functools
import typing as ta

from omlish import inject as inj
from omlish import lang

from ...configs import ChatConfig
from ..base import ChatInterface
from .configs import TextualInterfaceConfig
from .drivers.types import ChatDriverInterfaceGetter
from .drivers.types import ChatDriverInterfaceStateListener
from .types import ChatAppGetter


with lang.auto_proxy_import(globals()):
    from omdev import clipboard as cpb
    from omdev.tui import textual as tx

    from . import app as _app
    from . import inputhistory as _inputhistory
    from . import interface as _interface
    from . import suggestions as _suggestions
    from . import termrender as _termrender
    from .drivers import inject as _drivers
    from .drivers import interface as _interface2


##


async def _provide_chat_driver_interface(
        chat_cfg: ChatConfig,
        *,
        injector: inj.AsyncInjector,
        aes: contextlib.AsyncExitStack,
) -> ChatDriverInterfaceGetter:
    @contextlib.asynccontextmanager
    async def provide_child() -> ta.Any:
        async with contextlib.AsyncExitStack() as child_aes:
            ec = inj.collect_elements(inj.as_elements(
                inj.bind(contextlib.AsyncExitStack, to_const=child_aes),

                _drivers.bind_driver(
                    chat_cfg=chat_cfg,
                ),
            ))

            child_injector = await inj.create_async_injector(ec, parent=injector)

            yield await child_injector[ChatDriverInterfaceGetter]

    return await aes.enter_async_context(provide_child())


##


def bind_textual(
        cfg: TextualInterfaceConfig = TextualInterfaceConfig(),
        *,
        chat_cfg: ChatConfig = ChatConfig(),
) -> inj.Elements:
    els: list[inj.Elemental] = [
        inj.bind(ChatInterface, to_ctor=_interface.TextualChatInterface, singleton=True),
    ]

    #

    els.extend([
        inj.bind(_app.ChatApp, singleton=True),
        inj.bind_async_late(_app.ChatApp, ChatAppGetter),
    ])

    #

    els.extend([
        inj.bind(
            functools.partial(_provide_chat_driver_interface, chat_cfg),
            singleton=True,
        ),

        inj.bind(_interface2.ChatDriverInterface, to_async_fn=inj.target(g=ChatDriverInterfaceGetter)(lambda g: g())),
    ])

    #

    async def _app_driver_state_listener(ag: ChatAppGetter) -> ChatDriverInterfaceStateListener:
        async def fn(d, s):
            await (await ag())._on_driver_state_change(d, s)
        return ChatDriverInterfaceStateListener(fn)

    els.append(inj.bind(_app_driver_state_listener, singleton=True))

    #

    els.extend([
        inj.bind(cpb.Clipboard, to_fn=cpb.get_platform_clipboard, singleton=True),
    ])

    els.extend([
        inj.bind(tx.DevtoolsConfig(port=41932)),  # FIXME: lol

        inj.bind(
            tx.DevtoolsManager,
            singleton=True,
            to_async_fn=inj.make_async_managed_provider(
                tx.DevtoolsManager,
                contextlib.aclosing,  # noqa
            ),
        ),

        inj.bind(
            tx.DevtoolsSetup,
            to_async_fn=inj.target(mgr=tx.DevtoolsManager)(lambda mgr: mgr.get_setup()),
            singleton=True,
        ),
    ])

    #

    def _make_input_history_storage() -> _inputhistory.InputHistoryStorage:
        if cfg.input_history_file is not None:
            return _inputhistory.FileInputHistoryStorage(path=cfg.input_history_file)
        else:
            return _inputhistory.InMemoryInputHistoryStorage()

    els.extend([
        inj.bind(_inputhistory.InputHistoryStorage, to_fn=_make_input_history_storage, singleton=True),
        inj.bind(_inputhistory.InputHistoryManager, singleton=True),
    ])

    #

    els.extend([
        inj.bind(_suggestions.SuggestionsManager, singleton=True),
    ])

    #

    els.extend([
        inj.bind(_termrender.BackgroundTerminalRenderer, singleton=True),
    ])

    #

    return inj.as_elements(*els)
