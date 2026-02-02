import abc
import contextlib
import typing as ta

from .. import check
from .. import collections as col
from .. import lang
from ..logs import all as logs
from .debug import _ResourcesDebug


T = ta.TypeVar('T')
U = ta.TypeVar('U')

BaseResourceManagerT = ta.TypeVar('BaseResourceManagerT', bound='BaseResourceManager')


log = logs.get_module_logger(globals())


##


class ResourceManagerRef(lang.Abstract):
    pass


class ResourceManagerRefNotRegisteredError(Exception):
    pass


##


class BaseResourceManager(
    _ResourcesDebug,
    lang.Abstract,
    lang.NotPicklable,
    ta.Generic[T],
):
    """Essentially a reference-tracked [Async]ContextManager."""

    def __init__(
            self,
            *,
            init_ref: ResourceManagerRef | None = None,
            no_autoclose: bool = False,
    ) -> None:
        super().__init__()

        self._no_autoclose = no_autoclose

        self._closed = False

        self._refs: ta.MutableSet[ResourceManagerRef] = col.IdentitySet()

        if init_ref is not None:
            self.add_ref(init_ref)

    @abc.abstractmethod
    def init(self) -> T:
        raise NotImplementedError

    @property
    def autoclose(self) -> bool:
        return not self._no_autoclose

    @property
    def num_refs(self) -> int:
        return len(self._refs)

    @property
    def closed(self) -> bool:
        return self._closed

    def __repr__(self) -> str:
        return lang.attr_repr(self, 'closed', 'num_refs', with_id=True)

    #

    class _InitRef(ResourceManagerRef):
        pass

    #

    def add_ref(self, ref: ResourceManagerRef) -> None:
        check.isinstance(ref, ResourceManagerRef)
        check.state(not self._closed)

        self._refs.add(ref)

    def has_ref(self, ref: ResourceManagerRef) -> bool:
        return ref in self._refs

    @abc.abstractmethod
    def remove_ref(self, ref: ResourceManagerRef) -> T:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def enter_context(self, cm: ta.ContextManager[U]) -> U:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def new_managed(self, v: U) -> 'BaseResourceManaged[U, ta.Self]':
        raise NotImplementedError

    #

    def __del__(self) -> None:
        if not self._closed:
            ref_lst = list(self._refs)
            log.error(
                f'{__package__}.{self.__class__.__name__}.__del__: '  # noqa
                f'%r deleted without being closed! '
                f'refs: %s',
                repr(self),
                ref_lst,
            )


class BaseResourceManaged(
    ResourceManagerRef,
    _ResourcesDebug,
    lang.Abstract,
    lang.NotPicklable,
    ta.Generic[U, BaseResourceManagerT],
):
    """
    A class to 'handoff' a ref to a `BaseResourceManager`, allowing the `BaseResourceManager` to temporarily survive
    being passed from instantiation within a callee.

    This class wraps an arbitrary value, likely an object referencing resources managed by the `BaseResourceManager`,
    which is accessed by `__enter__/__aenter__`'ing. However, as the point of this class is handoff of a
    `BaseResourceManager`, not necessarily some arbitrary value, the value needn't necessarily be related to the
    `BaseResourceManager`, or may even be `None`.

    The ref to the `BaseResourceManager` is allocated in the ctor, so the contract is that an instance of this must be
    immediately `__enter__/__aenter__`'d before doing anything else with the return value of the call. Failure to do so
    leaks the `BaseResourceManager`.
    """

    def __init__(self, v: U, resources: BaseResourceManagerT) -> None:
        super().__init__()

        self._v = v
        self._resources = resources

        resources.add_ref(self)

    _state: ta.Literal['new', 'entered', 'exited'] = 'new'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<{self._v!r}, {self._state}>'

    def __del__(self) -> None:
        if self._state != 'exited':
            log.error(
                f'{__package__}.{self.__class__.__name__}.__del__: '  # noqa
                f'%r deleted without being entered and exited! '
                f'resources: %s',
                repr(self),
                repr(self._resources),
            )


##


@ta.final
class ResourceManager(
    BaseResourceManager[None],
    lang.Final,
):
    def __init__(
            self,
            *,
            init_ref: ResourceManagerRef | None = None,
            no_autoclose: bool = False,
    ) -> None:
        super().__init__(
            init_ref=init_ref,
            no_autoclose=no_autoclose,
        )

        self._es = contextlib.ExitStack()

    def init(self) -> None:
        self._es.__enter__()

        self._init_debug()

    #

    @classmethod
    def new(cls, **kwargs: ta.Any) -> ta.ContextManager['ResourceManager']:
        @contextlib.contextmanager
        def inner():
            init_ref = BaseResourceManager._InitRef()  # noqa

            res = ResourceManager(init_ref=init_ref, **kwargs)

            res.init()

            try:
                yield res

            finally:
                res.remove_ref(init_ref)

        return inner()

    @classmethod
    def or_new(
            cls,
            resources: ta.Optional['ResourceManager'],
            **kwargs: ta.Any,
    ) -> ta.ContextManager['ResourceManager']:
        if resources is None:
            return cls.new(**kwargs)

        @contextlib.contextmanager
        def inner():
            yield resources

        return inner()

    #

    def remove_ref(self, ref: ResourceManagerRef) -> None:
        check.isinstance(ref, ResourceManagerRef)

        try:
            self._refs.remove(ref)

        except KeyError:
            raise ResourceManagerRefNotRegisteredError(ref) from None

        if not self._no_autoclose and not self._refs:
            self.close()

    #

    def enter_context(self, cm: ta.ContextManager[U]) -> U:
        check.state(not self._closed)

        return self._es.enter_context(cm)

    #

    def new_managed(self, v: U) -> 'ResourceManaged[U]':
        return ResourceManaged(v, self)  # noqa

    #

    def close(self) -> None:
        try:
            self._es.__exit__(None, None, None)
        finally:
            self._closed = True


@ta.final
class ResourceManaged(
    BaseResourceManaged[U, ResourceManager],
    lang.Final,
    ta.ContextManager[U],
):
    def __enter__(self) -> U:
        check.state(self._state == 'new')
        self._state = 'entered'

        self._init_debug()

        return self._v

    def __exit__(self, exc_type, exc_val, exc_tb):
        check.state(self._state == 'entered')
        self._state = 'exited'

        self._resources.remove_ref(self)


##


@ta.final
class AsyncResourceManager(
    BaseResourceManager[ta.Awaitable[None]],
    lang.Final,
):
    def __init__(
            self,
            *,
            init_ref: ResourceManagerRef | None = None,
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
    def new(cls, **kwargs: ta.Any) -> ta.AsyncContextManager['AsyncResourceManager']:
        @contextlib.asynccontextmanager
        async def inner():
            init_ref = BaseResourceManager._InitRef()  # noqa

            res = AsyncResourceManager(init_ref=init_ref, **kwargs)

            await res.init()

            try:
                yield res

            finally:
                await res.remove_ref(init_ref)

        return inner()

    @classmethod
    def or_new(
            cls,
            resources: ta.Optional['AsyncResourceManager'],
            **kwargs: ta.Any,
    ) -> ta.AsyncContextManager['AsyncResourceManager']:
        if resources is None:
            return cls.new(**kwargs)

        @contextlib.asynccontextmanager
        async def inner():
            yield resources

        return inner()

    #

    async def remove_ref(self, ref: ResourceManagerRef) -> None:
        check.isinstance(ref, ResourceManagerRef)

        try:
            self._refs.remove(ref)

        except KeyError:
            raise ResourceManagerRefNotRegisteredError(ref) from None

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
    BaseResourceManaged[U, AsyncResourceManager],
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
