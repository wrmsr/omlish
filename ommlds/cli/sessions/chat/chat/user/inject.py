import typing as ta

from omlish import inject as inj
from omlish import lang

from ...... import minichain as mc
from ...phases.injection import phase_callbacks
from ...phases.types import ChatPhase
from ...phases.types import ChatPhaseCallback


with lang.auto_proxy_import(globals()):
    from ..state import types as _state
    from . import inputs as _inputs
    from . import interactive as _interactive
    from . import oneshot as _oneshot
    from . import types as _types


##


def bind_user(
        *,
        initial_system_content: ta.Optional['mc.Content'] = None,
        initial_user_content: ta.Optional['mc.Content'] = None,
        interactive: bool = False,
        use_readline: bool | ta.Literal['auto'] = False,
) -> inj.Elements:
    els: list[inj.Elemental] = []

    # FIXME: barf
    if initial_system_content is not None:
        async def add_initial_system_content(cm: '_state.ChatStateManager') -> None:
            await cm.extend_chat([mc.SystemMessage(initial_system_content)])

        els.append(phase_callbacks().bind_item(to_fn=lang.typed_lambda(cm=_state.ChatStateManager)(
            lambda cm: ChatPhaseCallback(ChatPhase.STARTED, lambda: add_initial_system_content(cm)),
        )))

    if interactive:
        if initial_user_content is not None:
            async def add_initial_user_content(cm: '_state.ChatStateManager') -> None:
                await cm.extend_chat([mc.UserMessage(initial_user_content)])

            els.append(phase_callbacks().bind_item(to_fn=lang.typed_lambda(cm=_state.ChatStateManager)(
                lambda cm: ChatPhaseCallback(ChatPhase.STARTED, lambda: add_initial_user_content(cm)),
            )))

            raise NotImplementedError

        els.append(inj.bind(_types.UserChatInput, to_ctor=_interactive.InteractiveUserChatInput, singleton=True))

        els.extend([
            inj.bind(_inputs.SyncStringInput, to_const=_inputs.InputSyncStringInput(use_readline=use_readline)),  # noqa
            inj.bind(_inputs.AsyncStringInput, to_ctor=_inputs.ThreadAsyncStringInput, singleton=True),
        ])

    else:
        if initial_user_content is None:
            raise ValueError('Initial user content is required for non-interactive chat')

        els.extend([
            inj.bind(_oneshot.OneshotUserChatInputInitialChat, to_const=[mc.UserMessage(initial_user_content)]),
            inj.bind(_types.UserChatInput, to_ctor=_oneshot.OneshotUserChatInput, singleton=True),
        ])

    return inj.as_elements(*els)
