from .. import dataclasses as _dc


_dc.init_package(
    globals(),
    codegen=True,
)


##


from .base import (  # noqa
    Lifecycle,
    AsyncLifecycle,
    AnyLifecycle,
    ANY_LIFECYCLE_TYPES,

    sync_to_async_lifecycle,
    as_async_lifecycle,
    async_to_sync_lifecycle,
    as_sync_lifecycle,

    CallbackLifecycle,
    CallbackAsyncLifecycle,
)

from .contextmanagers import (  # noqa
    ContextManagerLifecycle,
    AsyncContextManagerLifecycle,

    LifecycleContextManager,
    AsyncLifecycleContextManager,
)

from .controller import (  # noqa
    LifecycleController,
    AsyncLifecycleController,
    AnyLifecycleController,
    ANY_LIFECYCLE_CONTROLLER_TYPES,
)

from .listeners import (  # noqa
    LifecycleListener,
    AsyncLifecycleListener,
    AnyLifecycleListener,
    ANY_LIFECYCLE_LISTENER_TYPES,
)

from .managed import (  # noqa
    LifecycleManaged,
    AsyncLifecycleManaged,
    AnyLifecycleManaged,
    ANY_LIFECYCLE_MANAGED_TYPES,
)

from .manager import (  # noqa
    LifecycleManagerEntry,
    LifecycleManager,
    AsyncLifecycleManager,
)

from .states import (  # noqa
    LifecycleStateError,
    LifecycleState,
    LifecycleStates,
)

from .transitions import (  # noqa
    LifecycleTransition,
    LifecycleTransitions,
)

from .unwrap import (  # noqa
    unwrap_lifecycle,
    unwrap_async_lifecycle,
    unwrap_any_lifecycle,
)


##


from .. import lang as _lang  # noqa


with _lang.auto_proxy_init(globals()):
    ##

    from .injection import (  # noqa
        bind_lifecycle_registrar,
        bind_async_lifecycle_registrar,
    )
