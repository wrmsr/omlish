from omcore import inject as inj
from omcore import lang

from .types import PhaseCallback
from .types import PhaseCallbacks


##


@lang.cached_function
def phase_callbacks() -> inj.ItemsBinderHelper[PhaseCallback]:
    return inj.items_binder_helper[PhaseCallback](PhaseCallbacks)
