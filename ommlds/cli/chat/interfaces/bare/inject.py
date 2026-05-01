from omlish import inject as inj
from omlish import lang

from ..... import minichain as mc
from ...configs import ChatConfig
from ..base import ChatInterface
from .configs import BareInterfaceConfig


with lang.auto_proxy_import(globals()):
    from ....interfaces.bare.inputs import asyncs as _inputs_asyncs
    from ....interfaces.bare.inputs import sync as _inputs_sync
    from ....interfaces.bare.printing import inject as _printing2
    from ...backends import inject as _backends
    from ...drivers import inject as _drivers
    from . import chat as _chat
    from . import interactive as _interactive
    from . import oneshot as _oneshot
    from . import printing as _printing
    from . import tools as _tools


##


def bind_bare(
        cfg: BareInterfaceConfig = BareInterfaceConfig(),
        *,
        chat_cfg: ChatConfig = ChatConfig(),
) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        _backends.bind_backend(chat_cfg),

        _printing2.bind_printing(chat_cfg.printing),
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

    if cfg.interactive:
        els.extend([
            inj.bind(_interactive.InteractiveBareChatInterface, singleton=True),
            inj.bind(ChatInterface, to_key=_interactive.InteractiveBareChatInterface),
        ])

        els.extend([
            inj.bind(_inputs_sync.SyncStringInput, to_const=_inputs_sync.InputSyncStringInput(use_readline=cfg.use_readline)),  # noqa
            inj.bind(_inputs_asyncs.AsyncStringInput, to_ctor=_inputs_asyncs.ThreadAsyncStringInput, singleton=True),
        ])

    else:
        els.extend([
            inj.bind(_oneshot.OneshotBareChatInterface, singleton=True),
            inj.bind(ChatInterface, to_key=_oneshot.OneshotBareChatInterface),
        ])

    #

    if cfg.enable_tools:
        if cfg.dangerous_no_tool_confirmation:
            els.append(inj.bind(
                mc.drivers.ToolPermissionConfirmation,
                to_ctor=mc.drivers.UnsafeAlwaysAllowToolPermissionConfirmation,
                singleton=True,
            ))

        else:
            els.append(inj.bind(
                mc.drivers.ToolPermissionConfirmation,
                to_ctor=_tools.InteractiveToolPermissionConfirmation,
                singleton=True,
            ))

    #

    els.extend([
        inj.bind(_chat.BareUserInputSender, singleton=True),
        inj.bind(mc.facades.UserInputSender, to_key=_chat.BareUserInputSender),
    ])

    #

    els.extend([
        inj.bind(mc.facades.PrintMessageDisplayer, singleton=True),
        inj.bind(mc.facades.UiMessageDisplayer, to_key=mc.facades.PrintMessageDisplayer),
    ])

    #

    if cfg.print_ai_responses:
        if chat_cfg.driver.ai.stream:
            els.extend([
                inj.bind(_printing.AiStreamEventPrinter, singleton=True),

                mc.injection.event_callbacks().bind_item(
                    to_fn=inj.target(o=_printing.AiStreamEventPrinter)(lambda o: o.handle_event),
                ),
            ])

        else:
            els.extend([
                inj.bind(_printing.AiMessagesEventPrinter, singleton=True),

                mc.injection.event_callbacks().bind_item(
                    to_fn=inj.target(o=_printing.AiMessagesEventPrinter)(lambda o: o.handle_event),
                ),
            ])

    if cfg.print_tool_use:
        els.extend([
            inj.bind(_printing.ToolUseEventsPrinter, singleton=True),

            mc.injection.event_callbacks().bind_item(
                to_fn=inj.target(o=_printing.ToolUseEventsPrinter)(lambda o: o.handle_event),
            ),
        ])

    #

    return inj.as_elements(*els)
