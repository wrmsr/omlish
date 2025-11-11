from omlish import inject as inj
from omlish import lang

from ... import minichain as mc


with lang.auto_proxy_import(globals()):
    from . import types as _types


##


@lang.cached_function
def backend_configs() -> 'inj.ItemsBinderHelper[mc.Config]':
    return inj.items_binder_helper[mc.Config](_types.BackendConfigs)
