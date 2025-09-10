import typing as ta

from .. import lang
from .elements import Elemental
from .elements import as_elements
from .sync import Injector


with lang.auto_proxy_import(globals()):
    from .impl import maysync as _maysync


T = ta.TypeVar('T')


##


class MaysyncInjector(Injector, lang.Abstract):
    pass


##


def create_maysync_injector(*args: Elemental) -> MaysyncInjector:
    return _maysync.create_maysync_injector(as_elements(*args))
