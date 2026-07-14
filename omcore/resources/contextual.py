import typing as ta

from .. import contextual as cxl
from .managers import AsyncResourceManager
from .managers import ResourceManager


##


@cxl.wrap()
def contextual_or_new(
        *,
        resources: ResourceManager | None = cxl.param(None),
        **kwargs: ta.Any,
) -> ta.ContextManager[ResourceManager]:
    return ResourceManager.or_new(resources, **kwargs)


@cxl.wrap()
async def async_contextual_or_new(
        *,
        resources: AsyncResourceManager | None = cxl.param(None),
        **kwargs: ta.Any,
) -> ta.AsyncContextManager[AsyncResourceManager]:
    return AsyncResourceManager.or_new(resources, **kwargs)
