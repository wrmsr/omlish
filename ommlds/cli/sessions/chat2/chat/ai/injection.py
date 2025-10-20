from omlish import inject as inj
from omlish import lang

from ...... import minichain as mc


with lang.auto_proxy_import(globals()):
    from . import services as _services


##


@lang.cached_function
def chat_options() -> 'inj.ItemsBinderHelper[mc.ChatChoicesOption]':
    return inj.items_binder_helper[mc.ChatChoicesOption](_services.ChatChoicesServiceOptions)
