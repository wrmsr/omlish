"""
TODO:
 - inline WeakKeyDictionary
"""
import abc
import collections.abc
import typing as ta
import weakref

from .. import c3
from .. import check


T = ta.TypeVar('T')
U = ta.TypeVar('U')


##


def is_union_type(cls: ta.Any) -> bool:
    if hasattr(ta, 'UnionType'):
        return ta.get_origin(cls) in {ta.Union, getattr(ta, 'UnionType')}
    else:
        return ta.get_origin(cls) in {ta.Union}


_IMPL_FUNC_CLS_SET_CACHE: ta.MutableMapping[ta.Callable, ta.FrozenSet[type]] = weakref.WeakKeyDictionary()


def get_impl_func_cls_set(func: ta.Callable) -> ta.FrozenSet[type]:
    try:
        return _IMPL_FUNC_CLS_SET_CACHE[func]
    except KeyError:
        pass

    ann = getattr(func, '__annotations__', {})
    if not ann:
        raise TypeError(f'Invalid impl func: {func!r}')

    _, cls = next(iter(ta.get_type_hints(func).items()))
    if is_union_type(cls):
        ret = frozenset(check.isinstance(arg, type) for arg in ta.get_args(cls))
    else:
        ret = frozenset([check.isinstance(cls, type)])

    _IMPL_FUNC_CLS_SET_CACHE[func] = ret
    return ret


def find_impl(cls: type, registry: ta.Mapping[type, T]) -> ta.Optional[T]:
    mro = c3.compose_mro(cls, registry.keys())

    match: ta.Optional[type] = None
    for t in mro:
        if match is not None:
            # If *match* is an implicit ABC but there is another unrelated, equally matching implicit ABC, refuse the
            # temptation to guess.
            if (
                    t in registry
                    and t not in cls.__mro__
                    and match not in cls.__mro__
                    and not issubclass(match, t)
            ):
                raise RuntimeError(f'Ambiguous dispatch: {match} or {t}')
            break

        if t in registry:
            match = t

    return registry.get(match)


##


class WeakKeyDictionary(collections.abc.MutableMapping):
    """ Mapping class that references keys weakly.

    Entries in the dictionary will be discarded when there is no
    longer a strong reference to the key. This can be used to
    associate additional data with an object owned by other parts of
    an application without adding attributes to those objects. This
    can be especially useful with objects that override attribute
    accesses.
    """

    def __init__(self, dict=None):
        self.data = {}
        def remove(k, selfref=weakref.ref(self)):
            self = selfref()
            if self is not None:
                if self._iterating:
                    self._pending_removals.append(k)
                else:
                    try:
                        del self.data[k]
                    except KeyError:
                        pass
        self._remove = remove
        # A list of dead weakrefs (keys to be removed)
        self._pending_removals = []
        self._iterating = set()
        self._dirty_len = False
        if dict is not None:
            self.update(dict)

    def _commit_removals(self):
        # NOTE: We don't need to call this method before mutating the dict,
        # because a dead weakref never compares equal to a live weakref,
        # even if they happened to refer to equal objects.
        # However, it means keys may already have been removed.
        pop = self._pending_removals.pop
        d = self.data
        while True:
            try:
                key = pop()
            except IndexError:
                return

            try:
                del d[key]
            except KeyError:
                pass

    def _scrub_removals(self):
        d = self.data
        self._pending_removals = [k for k in self._pending_removals if k in d]
        self._dirty_len = False

    def __delitem__(self, key):
        self._dirty_len = True
        del self.data[ref(key)]

    def __getitem__(self, key):
        return self.data[weakref.ref(key)]

    def __len__(self):
        if self._dirty_len and self._pending_removals:
            # self._pending_removals may still contain keys which were
            # explicitly removed, we have to scrub them (see issue #21173).
            self._scrub_removals()
        return len(self.data) - len(self._pending_removals)

    def __repr__(self):
        return "<%s at %#x>" % (self.__class__.__name__, id(self))

    def __setitem__(self, key, value):
        self.data[weakref.ref(key, self._remove)] = value

    def copy(self):
        new = WeakKeyDictionary()
        with _IterationGuard(self):
            for key, value in self.data.items():
                o = key()
                if o is not None:
                    new[o] = value
        return new

    __copy__ = copy

    def __deepcopy__(self, memo):
        from copy import deepcopy
        new = self.__class__()
        with _IterationGuard(self):
            for key, value in self.data.items():
                o = key()
                if o is not None:
                    new[o] = deepcopy(value, memo)
        return new

    def get(self, key, default=None):
        return self.data.get(ref(key),default)

    def __contains__(self, key):
        try:
            wr = ref(key)
        except TypeError:
            return False
        return wr in self.data

    def items(self):
        with _IterationGuard(self):
            for wr, value in self.data.items():
                key = wr()
                if key is not None:
                    yield key, value

    def keys(self):
        with _IterationGuard(self):
            for wr in self.data:
                obj = wr()
                if obj is not None:
                    yield obj

    __iter__ = keys

    def values(self):
        with _IterationGuard(self):
            for wr, value in self.data.items():
                if wr() is not None:
                    yield value

    def keyrefs(self):
        """Return a list of weak references to the keys.

        The references are not guaranteed to be 'live' at the time
        they are used, so the result of calling the references needs
        to be checked before being used.  This can be used to avoid
        creating references that will cause the garbage collector to
        keep the keys around longer than needed.

        """
        return list(self.data)

    def popitem(self):
        self._dirty_len = True
        while True:
            key, value = self.data.popitem()
            o = key()
            if o is not None:
                return o, value

    def pop(self, key, *args):
        self._dirty_len = True
        return self.data.pop(ref(key), *args)

    def setdefault(self, key, default=None):
        return self.data.setdefault(ref(key, self._remove),default)

    def update(self, dict=None, /, **kwargs):
        d = self.data
        if dict is not None:
            if not hasattr(dict, "items"):
                dict = type({})(dict)
            for key, value in dict.items():
                d[ref(key, self._remove)] = value
        if len(kwargs):
            self.update(kwargs)

    def __ior__(self, other):
        self.update(other)
        return self

    def __or__(self, other):
        if isinstance(other, _collections_abc.Mapping):
            c = self.copy()
            c.update(other)
            return c
        return NotImplemented

    def __ror__(self, other):
        if isinstance(other, _collections_abc.Mapping):
            c = self.__class__()
            c.update(other)
            c.update(self)
            return c
        return NotImplemented


class Dispatcher(ta.Generic[T]):
    def __init__(self) -> None:
        super().__init__()

        impls_by_arg_cls: ta.Dict[type, T] = {}
        self._impls_by_arg_cls = impls_by_arg_cls

        dispatch_cache: ta.MutableMapping[type, ta.Optional[T]] = WeakKeyDictionary()
        self._dispatch_cache = dispatch_cache

        cache_token: ta.Any = None

        def dispatch(cls: type) -> ta.Optional[T]:
            nonlocal cache_token

            if cache_token is not None:
                current_token = abc.get_cache_token()
                if cache_token != current_token:
                    dispatch_cache.clear()
                    cache_token = current_token

            try:
                return dispatch_cache[cls]  # ~98ns
            except KeyError:
                pass

            try:
                impl = impls_by_arg_cls[cls]
            except KeyError:
                impl = find_impl(cls, impls_by_arg_cls)

            dispatch_cache[cls] = impl
            return impl

        self.dispatch = dispatch

        def register(impl: T, cls_col: ta.Iterable[type]) -> T:
            nonlocal cache_token

            for cls in cls_col:
                impls_by_arg_cls[cls] = impl  # type: ignore

                if cache_token is None and hasattr(cls, '__abstractmethods__'):
                    cache_token = abc.get_cache_token()

            self._dispatch_cache.clear()
            return impl

        self.register = register

    dispatch: ta.Callable[[type], ta.Optional[T]]

    register: ta.Callable[[U, ta.Iterable[type]], U]
