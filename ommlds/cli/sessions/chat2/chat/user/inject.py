from omlish import inject as inj
from omlish import lang

from ...... import minichain as mc


with lang.auto_proxy_import(globals()):
    from . import interactive as _interactive
    from . import oneshot as _oneshot
    from . import types as _types


##


def bind_rendering(
        *,
        initial_content: mc.Content | None = None,
        interactive: bool = False,
) -> inj.Elements:
    els: list[inj.Elemental] = []

    if interactive:
        if initial_content is not None:
            async def add_initial_content(cm: '_inj.ChatStateManager') -> None:
                await cm.extend_chat([mc.UserMessage(initial_content)])

            els.append(PHASE_CALLBACKS.bind_item(to_fn=lang.typed_lambda(cm=_inj.ChatStateManager)(
                lambda cm: _inj.ChatPhaseCallback(_inj.ChatPhase.STARTED, lambda: add_initial_content(cm)),
            )))

            raise NotImplementedError

        els.append(inj.bind(_types.UserChatInput, to_ctor=_interactive.InteractiveUserChatInput, singleton=True))

    else:
        if initial_content is None:
            raise ValueError('Initial content is required for non-interactive chat')

        els.extend([
            inj.bind(_oneshot.OneshotUserChatInputInitialChat, to_const=[mc.UserMessage(initial_content)]),
            inj.bind(_types.UserChatInput, to_ctor=_oneshot.OneshotUserChatInput, singleton=True),
        ])

    return inj.as_elements(*els)
