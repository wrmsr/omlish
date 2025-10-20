import typing as ta

from omlish import inject as inj
from omlish import lang

from .... import minichain as mc
from . import _inject as _inj
from .configs import DEFAULT_CHAT_MODEL_BACKEND
from .configs import ChatConfig
from .phases.injection import phase_callbacks


with lang.auto_proxy_import(globals()):
    from .chat.user import inject as _chat_user
    from .chat.state import inject as _chat_state
    from .phases import inject as _phases
    from .rendering import inject as _rendering


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
    ])

    #

    els.extend([
        _chat_user.bind_user(
            initial_content=cfg.initial_content,
            interactive=cfg.interactive,
        ),

        _chat_state.bind_state(
            state=cfg.state,
        ),

        _phases.bind_phases(),

        _rendering.bind_rendering(
            markdown=cfg.markdown,
        ),
    ])

    #

    if cfg.stream:
        ai_stack = inj.wrapper_binder_helper(_inj.StreamAiChatGenerator)

        els.append(ai_stack.push_bind(to_ctor=_inj.ChatChoicesStreamServiceStreamAiChatGenerator, singleton=True))

        if not cfg.silent:
            els.append(ai_stack.push_bind(to_ctor=_inj.RenderingStreamAiChatGenerator, singleton=True))

        els.extend([
            inj.bind(_inj.StreamAiChatGenerator, to_key=ai_stack.top),
            inj.bind(_inj.AiChatGenerator, to_key=_inj.StreamAiChatGenerator),
        ])

    else:
        ai_stack = inj.wrapper_binder_helper(_inj.AiChatGenerator)

        els.append(ai_stack.push_bind(to_ctor=_inj.ChatChoicesServiceAiChatGenerator, singleton=True))

        if not cfg.silent:
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
