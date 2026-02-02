import contextlib
import typing as ta

from .. import check
from .. import lang
from .base import BaseResourceManaged
from .base import BaseResources
from .base import ResourcesRef
from .errors import ResourcesRefNotRegisteredError


U = ta.TypeVar('U')


##


@ta.final
class AsyncResources(
    BaseResources[ta.Awaitable[None]],
    lang.Final,
):
    def __init__(
            self,
            *,
            init_ref: ResourcesRef | None = None,
            no_autoclose: bool = False,
    ) -> None:
        super().__init__(
            init_ref=init_ref,
            no_autoclose=no_autoclose,
        )

        self._aes = contextlib.AsyncExitStack()

    async def init(self) -> None:
        await self._aes.__aenter__()

        self._init_debug()

    #

    @classmethod
    def new(cls, **kwargs: ta.Any) -> ta.AsyncContextManager['AsyncResources']:
        @contextlib.asynccontextmanager
        async def inner():
            init_ref = BaseResources._InitRef()  # noqa

            res = AsyncResources(init_ref=init_ref, **kwargs)

            await res.init()

            try:
                yield res

            finally:
                await res.remove_ref(init_ref)

        return inner()

    @classmethod
    def or_new(
            cls,
            resources: ta.Optional['AsyncResources'],
            **kwargs: ta.Any,
    ) -> ta.AsyncContextManager['AsyncResources']:
        if resources is None:
            return cls.new(**kwargs)

        @contextlib.asynccontextmanager
        async def inner():
            yield resources

        return inner()

    #

    async def remove_ref(self, ref: ResourcesRef) -> None:
        check.isinstance(ref, ResourcesRef)

        try:
            self._refs.remove(ref)

        except KeyError:
            raise ResourcesRefNotRegisteredError(ref) from None

        if not self._no_autoclose and not self._refs:
            await self.aclose()

    #

    def enter_context(self, cm: ta.ContextManager[U]) -> U:
        check.state(not self._closed)

        return self._aes.enter_context(cm)

    async def enter_async_context(self, cm: ta.AsyncContextManager[U]) -> U:
        check.state(not self._closed)

        return await self._aes.enter_async_context(cm)

    #

    def new_managed(self, v: U) -> 'AsyncResourceManaged[U]':
        return AsyncResourceManaged(v, self)  # noqa

    #

    async def aclose(self) -> None:
        try:
            await self._aes.__aexit__(None, None, None)
        finally:
            self._closed = True


@ta.final
class AsyncResourceManaged(
    BaseResourceManaged[U, AsyncResources],
    lang.Final,
    ta.AsyncContextManager[U],
):
    async def __aenter__(self) -> U:
        check.state(self._state == 'new')
        self._state = 'entered'

        self._init_debug()

        return self._v

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        check.state(self._state == 'entered')
        self._state = 'exited'

        await self._resources.remove_ref(self)
