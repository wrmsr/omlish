import abc
import typing as ta

from .. import check
from .. import collections as col
from .. import lang
from ..logs import all as logs
from .debug import _ResourcesDebug


T = ta.TypeVar('T')
U = ta.TypeVar('U')

BaseResourcesT = ta.TypeVar('BaseResourcesT', bound='BaseResources')


log = logs.get_module_logger(globals())


##


class ResourcesRef(lang.Abstract):
    pass


class BaseResources(
    _ResourcesDebug,
    lang.Abstract,
    lang.NotPicklable,
    ta.Generic[T],
):
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


class BaseResourceManaged(
    ResourcesRef,
    _ResourcesDebug,
    lang.Abstract,
    lang.NotPicklable,
    ta.Generic[U, BaseResourcesT],
):
    """
    A class to 'handoff' a ref to a `Resources`, allowing the `Resources` to temporarily survive being passed from
    instantiation within a callee.

    This class wraps an arbitrary value, likely an object referencing resources managed by the `Resources`, which is
    accessed by `__enter__/__aenter__`'ing. However, as the point of this class is handoff of a `Resources`, not
    necessarily some arbitrary value, the value needn't necessarily be related to the `Resources`, or may even be
    `None`.

    The ref to the `Resources` is allocated in the ctor, so the contract is that an instance of this must be immediately
    `__enter__/__aenter__`'d before doing anything else with the return value of the call. Failure to do so leaks the
    `Resources`.
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
