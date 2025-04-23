# ruff: noqa: I001
import typing as _ta

from .. import lang as _lang


if _ta.TYPE_CHECKING:
    from . import api  # noqa
else:
    globals()['api'] = _lang.proxy_import('.api', __package__)

from .dbs import (  # noqa
    DbLoc,
    DbSpec,
    DbType,
    DbTypes,
    HostDbLoc,
    UrlDbLoc,
)

from .qualifiedname import (  # noqa
    QualifiedName,
    qn,
)

if _ta.TYPE_CHECKING:
    from . import queries  # noqa
else:
    globals()['queries'] = _lang.proxy_import('.queries', __package__)
