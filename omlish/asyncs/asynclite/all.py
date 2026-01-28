from ... import lang as _lang


with _lang.auto_proxy_import(globals()):
    from .anyio import all as anyio  # noqa
    from .asyncio import all as asyncio  # noqa
    from .sync import all as sync  # noqa


from .api import (  # noqa
    Asynclite as All,
)

from .base import (  # noqa
    AsyncliteObject as Object,
    AsyncliteApi as Api,

    AsyncliteCloseable as Closeable,
)

from .events import (  # noqa
    AsyncliteEvent as Event,
    AsyncliteEvents as Events,
)

from .identities import (  # noqa
    AsyncliteIdentities as Identities,
)

from .locks import (  # noqa
    AsyncliteLock as Lock,
    AsyncliteLocks as Locks,
)

from .queues import (  # noqa
    AsyncliteQueue as Queue,
    AsyncliteQueues as Queues,
)

from .semaphores import (  # noqa
    AsyncliteSemaphore as Semaphore,
    AsyncliteSemaphores as Semaphores,
)

from .sleeps import (  # noqa
    AsyncliteSleeps as Sleeps,
)
