from omlish import inject as inj
from omlish import lang

from .... import minichain as mc
from . import _inject as _inj
from .configs import DEFAULT_CHAT_MODEL_BACKEND
from .configs import ChatConfig


with lang.auto_proxy_import(globals()):
    from .backends import inject as _backends
    from .chat.ai import inject as _chat_ai
    from .chat.state import inject as _chat_state
    from .chat.user import inject as _chat_user
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
        _backends.bind_backends(
            backend=cfg.backend or DEFAULT_CHAT_MODEL_BACKEND,
        ),

        _chat_ai.bind_ai(
            stream=cfg.stream,
            silent=cfg.silent,
        ),

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

    els.append(inj.bind(_inj.ToolUseExecutor, to_ctor=_inj.ToolUseExecutorImpl, singleton=True))

    #

    els.extend([
        inj.bind(_inj.ChatDriver, singleton=True),
    ])

    #

    return inj.as_elements(*els)
