from omlish import inject as inj
from omlish import lang

from .services import ChatChoicesServiceOptionsProvider
from .services import ChatChoicesServiceOptionsProviders


##


@lang.cached_function
def chat_options_providers() -> inj.ItemsBinderHelper[ChatChoicesServiceOptionsProvider]:
    return inj.items_binder_helper[ChatChoicesServiceOptionsProvider](ChatChoicesServiceOptionsProviders)
