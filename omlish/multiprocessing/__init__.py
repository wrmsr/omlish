# ruff: noqa: I001
import typing as _ta

from .. import lang as _lang


from .proxies import (  # noqa
    DummyValueProxy,
    ValueProxy,
)

if _ta.TYPE_CHECKING:
    from .spawn import (  # noqa
        ExtrasSpawnContext,
        ExtrasSpawnPosixPopen,
        ExtrasSpawnProcess,
        SpawnExtras,
    )
else:
    _lang.proxy_init(globals(), '.spawn', [
        'ExtrasSpawnContext',
        'ExtrasSpawnPosixPopen',
        'ExtrasSpawnProcess',
        'SpawnExtras',
    ])
