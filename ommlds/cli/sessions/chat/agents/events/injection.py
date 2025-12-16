from omlish import inject as inj
from omlish import lang


with lang.auto_proxy_import(globals()):
    from . import types as _types


##


@lang.cached_function
def event_callbacks() -> 'inj.ItemsBinderHelper[_types.ChatEventCallback]':
    return inj.items_binder_helper[_types.ChatEventCallback](_types.ChatEventCallbacks)
