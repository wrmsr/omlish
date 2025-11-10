from omlish import inject as inj
from omlish import lang

from ...... import minichain as mc
from ...phases.injection import phase_callbacks
from ...phases.types import ChatPhase
from ...phases.types import ChatPhaseCallback
from .configs import UserConfig


with lang.auto_proxy_import(globals()):
    from .....inputs import asyncs as _inputs_asyncs
    from .....inputs import sync as _inputs_sync
    from ..state import types as _state
    from . import interactive as _interactive
    from . import oneshot as _oneshot
    from . import types as _types


##


def bind_user(cfg: UserConfig = UserConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    # FIXME: barf
    if cfg.initial_system_content is not None:
        async def add_initial_system_content(cm: '_state.ChatStateManager') -> None:
            await cm.extend_chat([mc.SystemMessage(cfg.initial_system_content)])

        els.append(phase_callbacks().bind_item(to_fn=lang.typed_lambda(cm=_state.ChatStateManager)(
            lambda cm: ChatPhaseCallback(ChatPhase.STARTED, lambda: add_initial_system_content(cm)),
        )))

    if cfg.interactive:
        if cfg.initial_user_content is not None:
            async def add_initial_user_content(cm: '_state.ChatStateManager') -> None:
                await cm.extend_chat([mc.UserMessage(cfg.initial_user_content)])

            els.append(phase_callbacks().bind_item(to_fn=lang.typed_lambda(cm=_state.ChatStateManager)(
                lambda cm: ChatPhaseCallback(ChatPhase.STARTED, lambda: add_initial_user_content(cm)),
            )))

            raise NotImplementedError

        els.append(inj.bind(_types.UserChatInput, to_ctor=_interactive.InteractiveUserChatInput, singleton=True))

        els.extend([
            inj.bind(_inputs_sync.SyncStringInput, to_const=_inputs_sync.InputSyncStringInput(use_readline=cfg.use_readline)),  # noqa
            inj.bind(_inputs_asyncs.AsyncStringInput, to_ctor=_inputs_asyncs.ThreadAsyncStringInput, singleton=True),
        ])

    else:
        if cfg.initial_user_content is None:
            raise ValueError('Initial user content is required for non-interactive chat')

        els.extend([
            inj.bind(_oneshot.OneshotUserChatInputInitialChat, to_const=[mc.UserMessage(cfg.initial_user_content)]),
            inj.bind(_types.UserChatInput, to_ctor=_oneshot.OneshotUserChatInput, singleton=True),
        ])

    return inj.as_elements(*els)
