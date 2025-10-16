import typing as ta

from omlish import inject as inj
from omlish import lang

from .... import minichain as mc
from . import _inject as _inj
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
        els.extend([
            inj.bind(_inj.StateStorageChatStateManager, singleton=True),
            inj.bind(_inj.ChatStateManager, to_key=_inj.StateStorageChatStateManager),
        ])

        if cfg.state == 'new':
            els.append(PHASE_CALLBACKS.bind_item(to_fn=lang.typed_lambda(cm=_inj.ChatStateManager)(
                lambda cm: _inj.ChatPhaseCallback(_inj.ChatPhase.STARTING, cm.clear_state),
            )))

    elif cfg.state == 'ephemeral':
        els.extend([
            inj.bind(_inj.InMemoryChatStateManager, singleton=True),
            inj.bind(_inj.ChatStateManager, to_key=_inj.InMemoryChatStateManager),
        ])

    else:
        raise TypeError(cfg.state)

    #

    els.extend([
        inj.bind(_inj.ToolUseExecutorImpl, singleton=True),
        inj.bind(_inj.ToolUseExecutor, to_key=_inj.ToolUseExecutorImpl),
    ])

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
