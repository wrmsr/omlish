from omlish import inject as inj
from omlish import lang


with lang.auto_proxy_import(globals()):
    from . import types as _types


##


@lang.cached_function
def system_message_providers() -> 'inj.ItemsBinderHelper[_types.SystemMessageProvider]':
    return inj.items_binder_helper[_types.SystemMessageProvider](_types.SystemMessageProviders)


@lang.cached_function
def placeholder_contents_providers() -> 'inj.ItemsBinderHelper[_types.PlaceholderContentsProvider]':
    return inj.items_binder_helper[_types.PlaceholderContentsProvider](_types.PlaceholderContentsProviders)
