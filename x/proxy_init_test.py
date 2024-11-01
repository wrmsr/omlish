import typing as _ta

from .proxy_init import proxy_init


if _ta.TYPE_CHECKING:
    from .timebuckets import (  # noqa
        DateBucketCounter,
    )
else:
    proxy_init(globals(), '.timebuckets', [
        'DateBucketCounter',
    ])

if _ta.TYPE_CHECKING:
    from .vt100 import (  # noqa
        STATE_TABLES,
    )
else:
    proxy_init(globals(), '.vt100', [
        'STATE_TABLES',
    ])
