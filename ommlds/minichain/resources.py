"""
TODO:
 - unify with omlish.sql.api.resources -> omlish.resources
"""
import contextlib
import threading
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


class Resources(lang.Final, lang.NotPicklable):
    def __init__(
            self,
            *,
            init_ref: ResourcesRef | None = None,
            no_autoclose: bool = False,
    ) -> None:
        super().__init__()

        self._no_autoclose = no_autoclose

        self._lock = threading.RLock()

        self._closed = False

        self._refs: ta.MutableSet[ResourcesRef] = col.IdentitySet()

        self._es = contextlib.ExitStack()
        self._es.__enter__()

        if init_ref is not None:
            self.add_ref(init_ref)

    @property
    def autoclose(self) -> bool:
        return not self._no_autoclose

    @property
    def num_refs(self) -> int:
        with self._lock:
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
    def new(cls, **kwargs: ta.Any) -> ta.ContextManager['Resources']:
        @contextlib.contextmanager
        def inner():
            init_ref = Resources._InitRef()
            res = Resources(init_ref=init_ref, **kwargs)
            try:
                yield res
            finally:
                res.remove_ref(init_ref)

        return inner()

    #

    def add_ref(self, ref: ResourcesRef) -> None:
        check.isinstance(ref, ResourcesRef)
        with self._lock:
            check.state(not self._closed)
            self._refs.add(ref)

    def has_ref(self, ref: ResourcesRef) -> bool:
        with self._lock:
            return ref in self._refs

    def remove_ref(self, ref: ResourcesRef) -> None:
        check.isinstance(ref, ResourcesRef)
        with self._lock:
            try:
                self._refs.remove(ref)
            except KeyError:
                raise ResourcesRefNotRegisteredError(ref) from None
            if not self._no_autoclose and not self._refs:
                self.close()

    #

    def enter_context(self, cm: ta.ContextManager[T]) -> T:
        with self._lock:
            check.state(not self._closed)
            return self._es.enter_context(cm)

    #

    def new_managed(self, v: T) -> 'ResourceManaged[T]':
        return ResourceManaged(v, self)

    #

    def close(self) -> None:
        with self._lock:
            try:
                self._es.__exit__(None, None, None)
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


class ResourceManaged(ResourcesRef, lang.Final, lang.NotPicklable, ta.Generic[T]):
    def __init__(self, v: T, resources: Resources) -> None:
        super().__init__()

        self._v = v
        self.__resources = resources

        resources.add_ref(self)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<{self._v!r}>'

    def __enter__(self) -> T:
        return self._v

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__resources.remove_ref(self)


##


class ResourcesOption(Option, lang.Abstract):
    pass


class UseResources(tv.UniqueScalarTypedValue[Resources], ResourcesOption, lang.Final):
    @classmethod
    @contextlib.contextmanager
    def or_new(cls, options: ta.Sequence[Option]) -> ta.Iterator[Resources]:
        if (ur := tv.as_collection(options).get(UseResources)) is not None:
            with ResourceManaged(ur.v, ur.v) as rs:
                yield rs
        else:
            with Resources.new() as rs:
                yield rs
