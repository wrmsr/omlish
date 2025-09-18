import typing as ta

from .. import lang
from .elements import Elemental
from .elements import as_elements
from .sync import Injector


if ta.TYPE_CHECKING:
    from .impl import maysync as _maysync
else:
    _maysync = lang.proxy_import('.impl.maysync', __package__)


T = ta.TypeVar('T')


##


class MaysyncInjector(Injector, lang.Abstract):
    pass


##


def create_maysync_injector(*args: Elemental) -> MaysyncInjector:
    return _maysync.create_maysync_injector(as_elements(*args))
