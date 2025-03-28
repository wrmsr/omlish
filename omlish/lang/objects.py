import types
import typing as ta
import weakref

from .classes.abstract import is_abstract_class


T = ta.TypeVar('T')


##


def attr_repr(
        obj: ta.Any,
        *attrs: str,
        with_module: bool = False,
        use_qualname: bool = False,
        with_id: bool = False,
) -> str:
    return (
        f'{obj.__class__.__module__ + "." if with_module else ""}'
        f'{obj.__class__.__qualname__ if use_qualname else obj.__class__.__name__}'
        f'{("@" + hex(id(obj))[2:]) if with_id else ""}'
        f'('
        f'{", ".join(f"{attr}={getattr(obj, attr)!r}" for attr in attrs)}'
        f')'
    )


def arg_repr(*args: ta.Any, **kwargs: ta.Any) -> str:
    return ', '.join(*(
        list(map(repr, args)) +
        [f'{k}={v!r}' for k, v in kwargs.items()]
    ))


def opt_repr(obj: ta.Any) -> str | None:
    if obj is None:
        return None
    return repr(obj)


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


def mro_owner_dict(
        instance_cls: type,
        owner_cls: type | None = None,
        *,
        bottom_up_key_order: bool = False,
        sort_keys: bool = False,
) -> ta.Mapping[str, tuple[type, ta.Any]]:
    if owner_cls is None:
        owner_cls = instance_cls

    mro = instance_cls.__mro__[-2::-1]
    try:
        pos = mro.index(owner_cls)
    except ValueError:
        raise TypeError(f'Owner class {owner_cls} not in mro of instance class {instance_cls}') from None

    dct: dict[str, tuple[type, ta.Any]] = {}
    if not bottom_up_key_order:
        for cur_cls in mro[:pos + 1][::-1]:
            for k, v in cur_cls.__dict__.items():
                if k not in dct:
                    dct[k] = (cur_cls, v)

    else:
        for cur_cls in mro[:pos + 1]:
            dct.update({k: (cur_cls, v) for k, v in cur_cls.__dict__.items()})

    if sort_keys:
        dct = dict(sorted(dct.items(), key=lambda t: t[0]))

    return dct


def mro_dict(
        instance_cls: type,
        owner_cls: type | None = None,
        *,
        bottom_up_key_order: bool = False,
        sort_keys: bool = False,
) -> ta.Mapping[str, ta.Any]:
    return {
        k: v
        for k, (o, v) in mro_owner_dict(
            instance_cls,
            owner_cls,
            bottom_up_key_order=bottom_up_key_order,
            sort_keys=sort_keys,
        ).items()
    }


def dir_dict(o: ta.Any) -> dict[str, ta.Any]:
    return {
        a: getattr(o, a)
        for a in dir(o)
    }


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
