from omlish import inject as inj
from omlish import lang

from .types import PlaceholderContentsProvider
from .types import PlaceholderContentsProviders
from .types import SystemMessageProvider
from .types import SystemMessageProviders


##


@lang.cached_function
def system_message_providers() -> inj.ItemsBinderHelper[SystemMessageProvider]:
    return inj.items_binder_helper[SystemMessageProvider](SystemMessageProviders)


@lang.cached_function
def placeholder_contents_providers() -> inj.ItemsBinderHelper[PlaceholderContentsProvider]:
    return inj.items_binder_helper[PlaceholderContentsProvider](PlaceholderContentsProviders)
