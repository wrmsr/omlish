import typing as ta

from omlish import inject as inj
from omlish import lang

from .... import minichain as mc
from . import _inject as _inj
from .configs import DEFAULT_CHAT_MODEL_BACKEND
from .configs import ChatConfig


ItemT = ta.TypeVar('ItemT')


##


CHAT_OPTIONS = inj.items_binder_helper[mc.ChatChoicesOption](_inj.ChatChoicesServiceOptions)
BACKEND_CONFIGS = inj.items_binder_helper[mc.Config](_inj.BackendConfigs)
PHASE_CALLBACKS = inj.items_binder_helper[_inj.ChatPhaseCallback](_inj.ChatPhaseCallbacks)


##


def bind_chat(cfg: ChatConfig) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        CHAT_OPTIONS.bind_items_provider(singleton=True),
        BACKEND_CONFIGS.bind_items_provider(singleton=True),
        PHASE_CALLBACKS.bind_items_provider(singleton=True),
    ])

    #

    if cfg.state in ('continue', 'new'):
        els.append(inj.bind(_inj.ChatStateManager, to_ctor=_inj.StateStorageChatStateManager, singleton=True))

        if cfg.state == 'new':
            els.append(PHASE_CALLBACKS.bind_item(to_fn=lang.typed_lambda(cm=_inj.ChatStateManager)(
                lambda cm: _inj.ChatPhaseCallback(_inj.ChatPhase.STARTING, cm.clear_state),
            )))

    elif cfg.state == 'ephemeral':
        els.append(inj.bind(_inj.ChatStateManager, to_ctor=_inj.InMemoryChatStateManager, singleton=True))

    else:
        raise TypeError(cfg.state)

    #

    if cfg.interactive:
        if cfg.initial_content is not None:
            async def add_initial_content(cm: '_inj.ChatStateManager') -> None:
                await cm.extend_chat([mc.UserMessage(cfg.initial_content)])

            els.append(PHASE_CALLBACKS.bind_item(to_fn=lang.typed_lambda(cm=_inj.ChatStateManager)(
                lambda cm: _inj.ChatPhaseCallback(_inj.ChatPhase.STARTED, lambda: add_initial_content(cm)),
            )))

            raise NotImplementedError

        els.append(inj.bind(_inj.UserChatInput, to_ctor=_inj.InteractiveUserChatInput, singleton=True))

    else:
        if cfg.initial_content is None:
            raise ValueError('Initial content is required for non-interactive chat')

        els.extend([
            inj.bind(_inj.OneshotUserChatInputInitialChat, to_const=[mc.UserMessage(cfg.initial_content)]),
            inj.bind(_inj.UserChatInput, to_ctor=_inj.OneshotUserChatInput, singleton=True),
        ])

    #

    if cfg.stream:
        ai_stack = inj.wrapper_binder_helper(_inj.StreamAiChatGenerator)

        els.append(ai_stack.push_bind(to_ctor=_inj.ChatChoicesStreamServiceStreamAiChatGenerator, singleton=True))

        if not cfg.silent:
            if cfg.markdown:
                els.append(inj.bind(_inj.StreamContentRendering, to_ctor=_inj.MarkdownStreamContentRendering, singleton=True))  # noqa

            else:
                els.append(inj.bind(_inj.StreamContentRendering, to_ctor=_inj.RawStreamContentRendering, singleton=True))  # noqa

            els.append(ai_stack.push_bind(to_ctor=_inj.RenderingStreamAiChatGenerator, singleton=True))

        els.extend([
            inj.bind(_inj.StreamAiChatGenerator, to_key=ai_stack.top),
            inj.bind(_inj.AiChatGenerator, to_key=_inj.StreamAiChatGenerator),
        ])

    else:
        ai_stack = inj.wrapper_binder_helper(_inj.AiChatGenerator)

        els.append(ai_stack.push_bind(to_ctor=_inj.ChatChoicesServiceAiChatGenerator, singleton=True))

        if not cfg.silent:
            if cfg.markdown:
                els.append(inj.bind(_inj.ContentRendering, to_ctor=_inj.MarkdownContentRendering, singleton=True))

            else:
                els.append(inj.bind(_inj.ContentRendering, to_ctor=_inj.RawContentRendering, singleton=True))

            els.append(ai_stack.push_bind(to_ctor=_inj.RenderingAiChatGenerator, singleton=True))

        els.append(inj.bind(_inj.AiChatGenerator, to_key=ai_stack.top))

    #

    els.append(inj.bind(_inj.BackendName, to_const=cfg.backend or DEFAULT_CHAT_MODEL_BACKEND))

    if cfg.stream:
        els.append(inj.bind(_inj.ChatChoicesStreamServiceBackendProvider, to_ctor=_inj.CatalogChatChoicesStreamServiceBackendProvider, singleton=True))  # noqa

    else:
        els.append(inj.bind(_inj.ChatChoicesServiceBackendProvider, to_ctor=_inj.CatalogChatChoicesServiceBackendProvider, singleton=True))  # noqa

    #

    els.append(inj.bind(_inj.ToolUseExecutor, to_ctor=_inj.ToolUseExecutorImpl, singleton=True))

    #

    els.extend([
        inj.bind(_inj.ChatPhaseManager, singleton=True),
    ])

    #

    els.extend([
        inj.bind(_inj.ChatDriver, singleton=True),
    ])

    #

    return inj.as_elements(*els)
