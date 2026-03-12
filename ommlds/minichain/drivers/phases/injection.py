from omlish import inject as inj
from omlish import lang

from .types import ChatPhaseCallback
from .types import ChatPhaseCallbacks


##


@lang.cached_function
def phase_callbacks() -> inj.ItemsBinderHelper[ChatPhaseCallback]:
    return inj.items_binder_helper[ChatPhaseCallback](ChatPhaseCallbacks)
