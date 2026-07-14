from omcore import inject as inj
from omcore import lang

from ..... import minichain as mc
from ...configs import ChatConfig
from ..base import ChatInterface
from .configs import WebInterfaceConfig
from .types import ServerPort


with lang.auto_proxy_import(globals()):
    from ...backends import inject as _backends
    from ...drivers import inject as _drivers
    from . import app as _app
    from . import interface as _interface
    from . import timelines as _timelines
    from . import userinput as _userinput
    from .chat import inject as _chat


##


def bind_web(
        cfg: WebInterfaceConfig = WebInterfaceConfig(),
        *,
        chat_cfg: ChatConfig = ChatConfig(),
) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        _backends.bind_backend(chat_cfg),
    ])

    #

    els.append(
        inj.override(
            _drivers.bind_driver(chat_cfg.driver, chat_cfg=chat_cfg),
        ),
    )

    #

    els.append(
        inj.override(
            mc.facades.inject.bind_facade(chat_cfg.facade),

            inj.bind(mc.facades.UiQuitSignal(mc.facades.RaiseUiQuitSignal(SystemExit))),
        ),
    )

    #

    els.append(mc.facades.timelines.inject.bind_timeline())

    # Facade ui notices flow into the timeline - and thus out to web clients.
    els.extend([
        inj.bind(mc.facades.EventEmittingUiMessageDisplayer, singleton=True),
        inj.bind(mc.facades.UiMessageDisplayer, to_key=mc.facades.EventEmittingUiMessageDisplayer),
    ])

    #

    els.extend([
        _chat.bind_chat(),
    ])

    #

    els.extend([
        inj.bind(_timelines.TimelineSseHandler, singleton=True),
        inj.bind(_userinput.UserInputHandler, singleton=True),
    ])

    #

    els.extend([
        inj.bind(_interface.WebChatInterface, singleton=True),
        inj.bind(ChatInterface, to_key=_interface.WebChatInterface),

        inj.bind(ServerPort, to_const=cfg.port),
    ])

    #

    els.extend([
        inj.bind(_app.ChatApp, singleton=True),
    ])

    #

    return inj.as_elements(*els)
