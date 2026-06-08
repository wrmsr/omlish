from omlish import inject as inj
from omlish import lang

from ...... import minichain as mc
from ....configs import ChatConfig
from ..configs import TextualInterfaceConfig
from .types import ChatDriverInterfaceGetter
from .types import InitialTimelineWindowLimit


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
            _drivers2.bind_driver(chat_cfg.driver, chat_cfg=chat_cfg),
        ),
    )

    #

    def _provide_quit_handler(cdi: ChatDriverInterfaceGetter) -> mc.facades.UiQuitSignal:
        async def inner() -> None:
            await (await cdi()).handle_quit()

        return mc.facades.UiQuitSignal(inner)

    els.append(
        inj.override(
            mc.facades.inject.bind_facade(chat_cfg.facade),

            inj.bind(_provide_quit_handler, singleton=True),
        ),
    )

    #

    els.extend([
        inj.bind(_interface.ChatDriverInterface, singleton=True),
        inj.bind_async_late(_interface.ChatDriverInterface, ChatDriverInterfaceGetter),
    ])

    #

    if chat_cfg.interface.enable_tools:
        els.append(inj.bind(
            mc.drivers.ToolPermissionConfirmation,
            to_ctor=_tools.ChatAppToolPermissionConfirmation,
            singleton=True,
        ))

    #

    els.append(mc.facades.timelines.inject.bind_timeline())

    if (
            isinstance(tic := chat_cfg.interface, TextualInterfaceConfig) and  # FIXME: ew
            (iwl := tic.initial_timeline_window) is not None
    ):
        els.append(inj.bind(InitialTimelineWindowLimit, to_const=InitialTimelineWindowLimit(iwl)))

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
