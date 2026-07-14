from omcore import inject as inj
from omcore import lang

from .presenting import TimelineItemPresenter
from .presenting import TimelineItemPresenters


##


@lang.cached_function
def timeline_item_presenters() -> inj.ItemsBinderHelper[TimelineItemPresenter]:
    return inj.items_binder_helper[TimelineItemPresenter](TimelineItemPresenters)
