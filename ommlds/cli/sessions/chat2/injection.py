from omlish import inject as inj
from omlish import lang

from .... import minichain as mc
from . import _inject as _inj


##


@lang.cached_function
def chat_options() -> 'inj.ItemsBinderHelper[mc.ChatChoicesOption]':
    return inj.items_binder_helper[mc.ChatChoicesOption](_inj.ChatChoicesServiceOptions)


@lang.cached_function
def backend_configs() -> 'inj.ItemsBinderHelper[mc.Config]':
    return inj.items_binder_helper[mc.Config](_inj.BackendConfigs)


@lang.cached_function
def phase_callbacks() -> 'inj.ItemsBinderHelper[_inj.ChatPhaseCallback]':
    return inj.items_binder_helper[_inj.ChatPhaseCallback](_inj.ChatPhaseCallbacks)
