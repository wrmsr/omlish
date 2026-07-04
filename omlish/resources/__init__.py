# fmt: off
# ruff: noqa: I001
from .. import lang as _lang


with _lang.auto_proxy_init(globals()):
    from .contextual import (  # noqa
        async_contextual_or_new,
        contextual_or_new,
    )

from .managers import (  # noqa
    ResourceManagerRef,
    ResourceManagerRefNotRegisteredError,

    BaseResourceManager,
    BaseResourceManaged,

    ResourceManager,
    ResourceManaged,

    AsyncResourceManager,
    AsyncResourceManaged,
)

from .debug import (  # noqa
    get_resource_debug,
    set_resource_debug,
)

from .exitstack import (  # noqa
    BaseKeyedExitStack,

    KeyedExitStack,

    AsyncKeyedExitStack,
)

from .errors import (  # noqa
    ResourceNotEnteredError,
    UnclosedResourceWarning,
)

from .simple import (  # noqa
    BaseSimpleResource,

    SimpleResource,

    AsyncSimpleResource,
)
