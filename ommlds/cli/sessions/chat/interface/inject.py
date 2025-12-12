from omlish import inject as inj
from omlish import lang

from .configs import InterfaceConfig

with lang.auto_proxy_import(globals()):
    from .textual import inject as _textual


##


def bind_interface(cfg: InterfaceConfig = InterfaceConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    _textual.bind_textual()  # FIXME lol

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
