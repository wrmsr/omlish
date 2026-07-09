import typing as ta

from omlish import lang
from omlish.inject.injector import AsyncInjector
from omlish.inject.keys import Key
from omlish.inject.scopes import SeededScope
from omlish.inject.scopes import async_enter_seeded_scope


if ta.TYPE_CHECKING:
    from . import maysync as _maysync
else:
    _maysync = lang.proxy_import('.maysync', __package__)


def maysync_enter_seeded_scope(
        i: _maysync.MaysyncInjector,
        ss: SeededScope,
        keys: ta.Mapping[Key, ta.Any],
) -> ta.ContextManager[None]:
    return lang.sync_async_with(async_enter_seeded_scope(
        i[AsyncInjector],
        ss,
        keys,
    ))
