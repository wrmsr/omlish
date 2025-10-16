import typing as ta

from omlish import inject as inj

from .... import minichain as mc
from . import _inject as _inj
from .configs import ChatConfig


ItemT = ta.TypeVar('ItemT')


##


CHAT_OPTIONS_BINDER_HELPER = inj.items_binder_helper[mc.ChatChoicesOption](_inj.ChatChoicesServiceOptions)
bind_chat_options = CHAT_OPTIONS_BINDER_HELPER.bind_items

BACKEND_CONFIGS_BINDER_HELPER = inj.items_binder_helper[mc.Config](_inj.BackendConfigs)
bind_backend_configs = BACKEND_CONFIGS_BINDER_HELPER.bind_items

PHASE_CALLBACKS_BINDER_HELPER = inj.items_binder_helper[_inj.ChatPhaseCallback](_inj.ChatPhaseCallbacks)
bind_chat_phase_callbacks = PHASE_CALLBACKS_BINDER_HELPER.bind_items


##


def bind_chat(cfg: ChatConfig) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        CHAT_OPTIONS_BINDER_HELPER.bind_items_provider(singleton=True),
        BACKEND_CONFIGS_BINDER_HELPER.bind_items_provider(singleton=True),
        PHASE_CALLBACKS_BINDER_HELPER.bind_items_provider(singleton=True),
    ])

    #

    els.extend([
        inj.bind(_inj.StateStorageChatStateManager, singleton=True),
        inj.bind(_inj.ChatStateManager, to_key=_inj.StateStorageChatStateManager),
    ])

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
