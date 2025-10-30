"""
TODO:
 - unify with omlish.sql.api.resources -> omlish.resources
"""
import contextlib
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import lang
from omlish import typedvalues as tv
from omlish.logs import all as logs

from .types import Option


T = ta.TypeVar('T')


log = logs.get_module_logger(globals())


##


class ResourcesRef(lang.Abstract):
    pass


class ResourcesRefNotRegisteredError(Exception):
    pass


@ta.final
class Resources(lang.Final, lang.NotPicklable):
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

        self._aes = contextlib.AsyncExitStack()

        if init_ref is not None:
            self.add_ref(init_ref)

    async def init(self) -> None:
        await self._aes.__aenter__()

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

    @classmethod
    def new(cls, **kwargs: ta.Any) -> ta.AsyncContextManager['Resources']:
        @contextlib.asynccontextmanager
        async def inner():
            init_ref = Resources._InitRef()
            res = Resources(init_ref=init_ref, **kwargs)
            await res.init()
            try:
                yield res
            finally:
                await res.remove_ref(init_ref)

        return inner()

    #

    def add_ref(self, ref: ResourcesRef) -> None:
        check.isinstance(ref, ResourcesRef)
        check.state(not self._closed)
        self._refs.add(ref)

    def has_ref(self, ref: ResourcesRef) -> bool:
        return ref in self._refs

    async def remove_ref(self, ref: ResourcesRef) -> None:
        check.isinstance(ref, ResourcesRef)
        try:
            self._refs.remove(ref)
        except KeyError:
            raise ResourcesRefNotRegisteredError(ref) from None
        if not self._no_autoclose and not self._refs:
            await self.aclose()

    #

    def enter_context(self, cm: ta.ContextManager[T]) -> T:
        check.state(not self._closed)
        return self._aes.enter_context(cm)

    async def enter_async_context(self, cm: ta.AsyncContextManager[T]) -> T:
        check.state(not self._closed)
        return await self._aes.enter_async_context(cm)

    #

    def new_managed(self, v: T) -> 'ResourceManaged[T]':
        return ResourceManaged(v, self)

    #

    async def aclose(self) -> None:
        try:
            await self._aes.__aexit__(None, None, None)
        finally:
            self._closed = True

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


##


@ta.final
class ResourceManaged(ResourcesRef, lang.Final, lang.NotPicklable, ta.Generic[T]):
    """
    A class to 'handoff' a ref to a `Resources`, allowing the `Resources` to temporarily survive being passed from
    instantiation within a callee to being `__aenter__`'d in the caller.

    The ref to the `Resources` is allocated in the ctor, so the contract is that an instance of this must be immediately
    `__aenter__`'d before doing anything else with the return value of the call. Failure to do so leaks the `Resources`.
    """

    def __init__(self, v: T, resources: Resources) -> None:
        super().__init__()

        self.__v = v
        self.__resources = resources

        resources.add_ref(self)

    __state: ta.Literal['new', 'entered', 'exited'] = 'new'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<{self.__v!r}, {self.__state}>'

    async def __aenter__(self) -> T:
        check.state(self.__state == 'new')
        self.__state = 'entered'
        return self.__v

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        check.state(self.__state == 'entered')
        self.__state = 'exited'
        await self.__resources.remove_ref(self)

    def __del__(self) -> None:
        if self.__state != 'exited':
            log.error(
                f'{__package__}.{self.__class__.__name__}.__del__: '  # noqa
                f'%r deleted without being entered and exited! '
                f'resources: %s',
                repr(self),
                repr(self.__resources),
            )

##


class ResourcesOption(Option, lang.Abstract):
    pass


class UseResources(tv.UniqueScalarTypedValue[Resources], ResourcesOption, lang.Final):
    @classmethod
    @contextlib.asynccontextmanager
    async def or_new(cls, options: ta.Sequence[Option]) -> ta.AsyncGenerator[Resources]:
        if (ur := tv.as_collection(options).get(UseResources)) is not None:
            async with ResourceManaged(ur.v, ur.v) as rs:
                yield rs
        else:
            async with Resources.new() as rs:
                yield rs
