"""
TODO:
 - unify with omlish.sql.api.resources -> omlish.resources
"""
import abc
import contextlib
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import lang
from omlish.logs import all as logs


T = ta.TypeVar('T')
U = ta.TypeVar('U')

BaseResourcesT = ta.TypeVar('BaseResourcesT', bound='BaseResources')


log = logs.get_module_logger(globals())


##


class ResourcesRef(lang.Abstract):
    pass


class ResourcesRefNotRegisteredError(Exception):
    pass


class BaseResources(lang.Abstract, lang.NotPicklable, ta.Generic[T]):
    """Essentially a reference-tracked [Async]ContextManager."""

    def __init__(
            self,
            *,
            init_ref: ResourcesRef | None = None,
            no_autoclose: bool = False,
    ) -> None:
        super().__init__()

        self._no_autoclose = no_autoclose

        self._closed = False

        self._refs: ta.MutableSet[ResourcesRef] = col.IdentitySet()

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

    class _InitRef(ResourcesRef):
        pass

    #

    def add_ref(self, ref: ResourcesRef) -> None:
        check.isinstance(ref, ResourcesRef)
        check.state(not self._closed)

        self._refs.add(ref)

    def has_ref(self, ref: ResourcesRef) -> bool:
        return ref in self._refs

    @abc.abstractmethod
    def remove_ref(self, ref: ResourcesRef) -> T:
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


class BaseResourceManaged(ResourcesRef, lang.Abstract, lang.NotPicklable, ta.Generic[U, BaseResourcesT]):
    """
    A class to 'handoff' a ref to a `Resources`, allowing the `Resources` to temporarily survive being passed from
    instantiation within a callee.

    This class wraps an arbitrary value, likely an object referencing resources managed by the `Resources`, which is
    accessed by `__aenter__`'ing. However, as the point of this class is handoff of a `Resources`, not necessarily some
    arbitrary value, the value needn't necessarily be related to the `Resources`, or may even be `None`.

    The ref to the `Resources` is allocated in the ctor, so the contract is that an instance of this must be immediately
    `__aenter__`'d before doing anything else with the return value of the call. Failure to do so leaks the `Resources`.
    """

    def __init__(self, v: U, resources: BaseResourcesT) -> None:
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
class Resources(BaseResources[None], lang.Final):
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

        self._es = contextlib.ExitStack()

    def init(self) -> None:
        self._es.__enter__()

    #

    @classmethod
    def new(cls, **kwargs: ta.Any) -> ta.ContextManager['Resources']:
        @contextlib.contextmanager
        def inner():
            init_ref = BaseResources._InitRef()

            res = Resources(init_ref=init_ref, **kwargs)

            res.init()

            try:
                yield res

            finally:
                res.remove_ref(init_ref)

        return inner()

    #

    def remove_ref(self, ref: ResourcesRef) -> None:
        check.isinstance(ref, ResourcesRef)

        try:
            self._refs.remove(ref)

        except KeyError:
            raise ResourcesRefNotRegisteredError(ref) from None

        if not self._no_autoclose and not self._refs:
            self.close()

    #

    def enter_context(self, cm: ta.ContextManager[U]) -> U:
        check.state(not self._closed)

        return self._es.enter_context(cm)

    #

    def new_managed(self, v: U) -> 'ResourceManaged[U]':
        return ResourceManaged(v, self)

    #

    def close(self) -> None:
        try:
            self._es.__exit__(None, None, None)
        finally:
            self._closed = True


@ta.final
class ResourceManaged(BaseResourceManaged[U, Resources], lang.Final):
    def __enter__(self) -> U:
        check.state(self._state == 'new')
        self._state = 'entered'

        return self._v

    def __exit__(self, exc_type, exc_val, exc_tb):
        check.state(self._state == 'entered')
        self._state = 'exited'

        self._resources.remove_ref(self)


##


@ta.final
class AsyncResources(BaseResources[ta.Awaitable[None]], lang.Final):
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

    #

    @classmethod
    def new(cls, **kwargs: ta.Any) -> ta.AsyncContextManager['AsyncResources']:
        @contextlib.asynccontextmanager
        async def inner():
            init_ref = BaseResources._InitRef()

            res = AsyncResources(init_ref=init_ref, **kwargs)

            await res.init()

            try:
                yield res

            finally:
                await res.remove_ref(init_ref)

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
        return AsyncResourceManaged(v, self)

    #

    async def aclose(self) -> None:
        try:
            await self._aes.__aexit__(None, None, None)
        finally:
            self._closed = True


@ta.final
class AsyncResourceManaged(BaseResourceManaged[U, AsyncResources], lang.Final):
    async def __aenter__(self) -> U:
        check.state(self._state == 'new')
        self._state = 'entered'

        return self._v

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        check.state(self._state == 'entered')
        self._state = 'exited'

        await self._resources.remove_ref(self)
