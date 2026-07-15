import contextlib
import typing as ta

from .. import contextual as cxl
from .managers import AsyncResourceManaged
from .managers import AsyncResourceManager
from .managers import ResourceManaged
from .managers import ResourceManager


##


@cxl.wrap()
def contextual_or_new(
        *,
        bind: bool = False,
        resources: ResourceManager | None = cxl.param(None),
        **kwargs: ta.Any,
) -> ta.ContextManager[ResourceManager]:
    if resources is not None:
        return ResourceManaged(resources, resources)

    if not bind:
        return ResourceManager.new(**kwargs)

    @contextlib.contextmanager
    def inner():
        with ResourceManager.new(**kwargs) as resources:  # noqa
            with cxl.bind({ResourceManager: resources}):
                yield resources

    return inner()


@cxl.wrap()
async def async_contextual_or_new(
        *,
        bind: bool = False,
        resources: AsyncResourceManager | None = cxl.param(None),
        **kwargs: ta.Any,
) -> ta.AsyncContextManager[AsyncResourceManager]:
    if resources is not None:
        return AsyncResourceManaged(resources, resources)

    if not bind:
        return AsyncResourceManager.new(**kwargs)

    @contextlib.asynccontextmanager
    async def inner():
        async with AsyncResourceManager.new(**kwargs) as resources:  # noqa
            with cxl.bind({AsyncResourceManager: resources}):
                yield resources

    return inner()
