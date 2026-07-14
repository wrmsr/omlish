from omcore import inject as inj
from omcore import lang

from .types import EventCallback
from .types import EventCallbacks


##


@lang.cached_function
def event_callbacks() -> inj.ItemsBinderHelper[EventCallback]:
    return inj.items_binder_helper[EventCallback](EventCallbacks)
