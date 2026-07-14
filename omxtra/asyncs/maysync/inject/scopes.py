import typing as ta

from omcore import lang
from omcore.inject.injector import AsyncInjector
from omcore.inject.keys import Key
from omcore.inject.scopes import SeededScope
from omcore.inject.scopes import async_enter_seeded_scope


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
