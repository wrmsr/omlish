from omlish import inject as inj
from omlish import lang


with lang.auto_proxy_import(globals()):
    from . import services as _services


##


@lang.cached_function
def chat_options_providers() -> 'inj.ItemsBinderHelper[_services.ChatChoicesServiceOptionsProvider]':
    return inj.items_binder_helper[_services.ChatChoicesServiceOptionsProvider](_services.ChatChoicesServiceOptionsProviders)  # noqa
