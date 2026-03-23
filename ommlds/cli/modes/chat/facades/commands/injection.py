from omlish import inject as inj
from omlish import lang


with lang.auto_proxy_import(globals()):
    from . import base as _base
    from . import types as _types


##


@lang.cached_function
def commands() -> 'inj.ItemsBinderHelper[_base.Command]':
    return inj.items_binder_helper[_base.Command](_types.Commands)
