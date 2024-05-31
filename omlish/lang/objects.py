import types
import typing as ta


T = ta.TypeVar('T')


##


def attr_repr(obj: ta.Any, *attrs: str) -> str:
    return '%s(%s)' % (
        type(obj).__name__,
        ', '.join('%s=%r' % (attr, getattr(obj, attr)) for attr in attrs))


def arg_repr(*args, **kwargs) -> str:
    return ', '.join(*(
        list(map(repr, args)) +
        [f'{k}={repr(v)}' for k, v in kwargs.items()]
    ))


##


def new_type(
        name: str,
        bases: ta.Sequence[ta.Any],
        namespace: ta.Mapping[str, ta.Any],
        **kwargs
) -> ta.Type:
    return types.new_class(
        name,
        tuple(bases),
        kwds=kwargs,
        exec_body=lambda ns: ns.update(namespace),
    )


def super_meta(
        super_meta: ta.Any,
        meta: ta.Type,
        name: str,
        bases: ta.Sequence[ta.Any],
        namespace: ta.MutableMapping[str, ta.Any],
        **kwargs
) -> ta.Type:
    """Per types.new_class"""
    resolved_bases = types.resolve_bases(bases)
    if resolved_bases is not bases:
        if '__orig_bases__' in namespace:
            raise TypeError((bases, resolved_bases))
        namespace['__orig_bases__'] = bases
    return super_meta.__new__(meta, name, resolved_bases, dict(namespace), **kwargs)


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

        def __delete__(self, instance):
            if instance is None:
                return self
            delattr(object.__getattribute__(instance, '__wrapped__'), self._attr)

    __wrapped_attrs__: ta.Iterable[str] = set()

    def __init__(self, wrapped: T) -> None:
        super().__init__()
        object.__setattr__(self, '__wrapped__', wrapped)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        for attr in cls.__wrapped_attrs__:
            setattr(cls, attr, SimpleProxy.Descriptor(attr))

    def __getattr__(self, item):
        return getattr(object.__getattribute__(self, '__wrapped__'), item)

    def __setattr__(self, name, value):
        setattr(object.__getattribute__(self, '__wrapped__'), name, value)

    def __delattr__(self, item):
        delattr(object.__getattribute__(self, '__wrapped__'), item)
