import asyncio

from omlish import inject as inj
from omlish import lang

from ...... import minichain as mc
from ....configs import ChatConfig
from ..configs import TextualInterfaceConfig
from .types import ChatDriverInterfaceGetter


with lang.auto_proxy_import(globals()):
    from ....backends import inject as _backends
    from ....drivers import inject as _drivers2
    from . import chat as _chat
    from . import facades as _facades
    from . import interface as _interface
    from . import tools as _tools
    from . import welcome as _welcome


##


def bind_driver_internal(
        cfg: TextualInterfaceConfig = TextualInterfaceConfig(),
        *,
        chat_cfg: ChatConfig = ChatConfig(),
) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        _backends.bind_backend(chat_cfg),

        _drivers2.bind_driver(chat_cfg.driver, chat_cfg=chat_cfg),

        mc.facades.inject.bind_facade(chat_cfg.facade),
    ])

    #

    els.extend([
        inj.bind(_interface.ChatDriverInterface, singleton=True),
        inj.bind_async_late(_interface.ChatDriverInterface, ChatDriverInterfaceGetter),
    ])

    #

    if cfg.enable_tools:
        els.append(inj.bind(
            mc.drivers.ToolPermissionConfirmation,
            to_ctor=_tools.ChatAppToolPermissionConfirmation,
            singleton=True,
        ))

    #

    els.extend([
        inj.bind(_interface.ChatEventQueue, to_const=asyncio.Queue()),

        mc.drivers.injection.event_callbacks().bind_item(to_fn=inj.target(eq=_interface.ChatEventQueue)(lambda eq: lambda ev: eq.put(ev))),  # noqa
    ])

    #

    els.append(inj.bind(_welcome.build_welcome_message, singleton=True))

    #

    els.extend([
        inj.bind(_chat.TextualUserInputSender, singleton=True),
        inj.bind(mc.facades.UserInputSender, to_key=_chat.TextualUserInputSender),
    ])

    #

    els.extend([
        inj.bind(_facades.ChatAppUiMessageDisplayer, singleton=True),
        inj.bind(mc.facades.UiMessageDisplayer, to_key=_facades.ChatAppUiMessageDisplayer),
    ])

    #

    return inj.as_elements(*els)


def bind_driver(
        cfg: TextualInterfaceConfig = TextualInterfaceConfig(),
        *,
        chat_cfg: ChatConfig = ChatConfig(),
) -> inj.Elements:
    return inj.as_elements(
        inj.private(
            bind_driver_internal(cfg, chat_cfg=chat_cfg),

            inj.expose(inj.as_key(_interface.ChatDriverInterface)),
            inj.expose(inj.as_key(ChatDriverInterfaceGetter)),
        ),
    )
