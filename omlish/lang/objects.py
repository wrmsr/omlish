import types
import typing as ta
import weakref

from ..lite.maybes import Maybe
from .classes.abstract import is_abstract_class


T = ta.TypeVar('T')


##


def arg_repr(*args: ta.Any, **kwargs: ta.Any) -> str:
    return ', '.join(*(
        list(map(repr, args)) +
        [f'{k}={v!r}' for k, v in kwargs.items()]
    ))


def opt_repr(obj: ta.Any) -> str | None:
    return repr(obj) if obj is not None else None


def truthy_repr(o: ta.Any) -> str | None:
    return repr(o) if o else None


def just_repr(obj: Maybe) -> str | None:
    return obj.map(repr).or_none()


def opt_or_just_repr(obj: ta.Any) -> str | None:
    if isinstance(obj, Maybe):
        if obj.present:
            return repr(obj)
        return None
    return opt_repr(obj)


##


_CAN_WEAKREF_TYPE_MAP: ta.MutableMapping[type, bool] = weakref.WeakKeyDictionary()


def can_weakref(obj: ta.Any) -> bool:
    _type = type(obj)
    try:
        return _CAN_WEAKREF_TYPE_MAP[_type]
    except KeyError:
        pass
    try:
        weakref.ref(obj)
    except TypeError:
        ret = False
    else:
        ret = True
    _CAN_WEAKREF_TYPE_MAP[_type] = ret
    return ret


##


def new_type(
        name: str,
        bases: ta.Sequence[ta.Any],
        namespace: ta.Mapping[str, ta.Any],
        **kwargs: ta.Any,
) -> type:
    return types.new_class(
        name,
        tuple(bases),
        kwds=kwargs,
        exec_body=lambda ns: ns.update(namespace),
    )


def super_meta(
        super_meta: ta.Any,
        meta: type,
        name: str,
        bases: ta.Sequence[ta.Any],
        namespace: ta.MutableMapping[str, ta.Any],
        **kwargs: ta.Any,
) -> type:
    """Per types.new_class"""

    resolved_bases = types.resolve_bases(bases)
    if resolved_bases is not bases:
        if '__orig_bases__' in namespace:
            raise TypeError((bases, resolved_bases))
        namespace['__orig_bases__'] = bases
    return super_meta.__new__(meta, name, resolved_bases, dict(namespace), **kwargs)


##


def deep_subclasses(
        cls: type[T],
        *,
        concrete_only: bool = False,
) -> ta.Iterator[type[T]]:
    seen = set()
    todo = list(reversed(cls.__subclasses__()))
    while todo:
        cur = todo.pop()
        if cur in seen:
            continue
        seen.add(cur)
        if not (concrete_only and is_abstract_class(cur)):
            yield cur
        todo.extend(reversed(cur.__subclasses__()))


def deep_subclass_tree(
        cls: type[T],
        *,
        total: bool = False,
        concrete_only: bool = False,
) -> dict[type[T], set[type[T]]]:
    # Stores the "total" descendants for each class visited
    memo: dict[type[T], set[type[T]]] = {}
    # Tracks the current path to detect cycles
    visiting: set[type[T]] = set()

    def walk(current: type[T]) -> set[type[T]]:
        if current in memo:
            return memo[current]

        if current in visiting:
            # Cycle detected: return empty set to break recursion
            return set()

        visiting.add(current)
        all_descendants = set()

        try:
            for sub in current.__subclasses__():
                # Add the child and all of the child's descendants
                all_descendants.add(sub)
                all_descendants.update(walk(sub))
        finally:
            visiting.remove(current)

        memo[current] = all_descendants
        return all_descendants

    # Execute the traversal
    walk(cls)

    # Transform memo into the requested output format
    final_output: dict[type[T], set[type[T]]] = {}

    for klass, descendants in memo.items():
        # Select base set: total vs immediate
        source_set = descendants if total else set(klass.__subclasses__())

        # Apply concrete filter if requested
        if concrete_only:
            final_output[klass] = {d for d in source_set if not is_abstract_class(d)}
        else:
            final_output[klass] = source_set

    return final_output


##


class SimpleProxy(ta.Generic[T]):
    class Descriptor:
        def __init__(self, attr: str) -> None:
            super().__init__()

            self._attr = attr

        def __get__(self, instance, owner=None):
            if instance is None:
                return self
            return getattr(object.__getattribute__(instance, '__wrapped__'), self._attr)

        def __set__(self, instance, value):
            if instance is None:
                return self
            setattr(object.__getattribute__(instance, '__wrapped__'), self._attr, value)
            return None

        def __delete__(self, instance):
            if instance is None:
                return self
            delattr(object.__getattribute__(instance, '__wrapped__'), self._attr)
            return None

    __wrapped_attrs__: ta.ClassVar[ta.Iterable[str]] = ()

    def __init__(self, wrapped: T) -> None:
        super().__init__()

        object.__setattr__(self, '__wrapped__', wrapped)

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        for attr in cls.__wrapped_attrs__:
            setattr(cls, attr, SimpleProxy.Descriptor(attr))

    def __getattr__(self, item):
        return getattr(object.__getattribute__(self, '__wrapped__'), item)

    def __setattr__(self, name, value):
        setattr(object.__getattribute__(self, '__wrapped__'), name, value)

    def __delattr__(self, item):
        delattr(object.__getattribute__(self, '__wrapped__'), item)


##


class _AnonObject:
    def __init__(self, **attrs: ta.Any) -> None:
        super().__init__()

        for k, v in attrs.items():
            setattr(self, k, v)

    def __init_subclass__(cls, **kwargs):
        raise TypeError


def anon_object(**attrs: ta.Any) -> ta.Any:
    return _AnonObject(**attrs)


##


class Identity(ta.Generic[T]):
    def __init__(self, obj: T) -> None:
        super().__init__()

        self._obj = obj

    def __bool__(self):
        raise TypeError

    @property
    def obj(self) -> T:
        return self._obj

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._obj!r})'

    def __hash__(self) -> int:
        return id(self._obj)

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return self._obj is other._obj  # noqa

    def __ne__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return self._obj is not other._obj  # noqa
