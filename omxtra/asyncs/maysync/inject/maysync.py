import typing as ta

from omlish import lang
from omlish.inject.injector import _InjectorCreator
from omlish.inject.sync import Injector


if ta.TYPE_CHECKING:
    from .impl import maysync as _maysync
else:
    _maysync = lang.proxy_import('.impl.maysync', __package__)


T = ta.TypeVar('T')


##


class MaysyncInjector(Injector, lang.Abstract):
    pass


##


create_maysync_injector = _InjectorCreator[MaysyncInjector, MaysyncInjector](
    lambda ce, p=None: _maysync.create_maysync_injector(ce, p),
)
