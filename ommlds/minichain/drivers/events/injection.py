from omlish import inject as inj
from omlish import lang

from .types import ChatEventCallback
from .types import ChatEventCallbacks


##


@lang.cached_function
def event_callbacks() -> inj.ItemsBinderHelper[ChatEventCallback]:
    return inj.items_binder_helper[ChatEventCallback](ChatEventCallbacks)
