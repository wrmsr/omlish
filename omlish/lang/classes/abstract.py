import abc
import typing as ta


T = ta.TypeVar('T')


_DISABLE_CHECKS = False

_ABSTRACT_METHODS_ATTR = '__abstractmethods__'
_IS_ABSTRACT_METHOD_ATTR = '__isabstractmethod__'
_FORCE_ABSTRACT_ATTR = '__forceabstract__'

_INTERNAL_ABSTRACT_ATTRS = frozenset([_FORCE_ABSTRACT_ATTR])


def make_abstract(obj: T) -> T:
    if callable(obj):
        return ta.cast(T, abc.abstractmethod(obj))
    elif isinstance(obj, property):
        return ta.cast(T, property(
            abc.abstractmethod(obj.fget) if obj.fget is not None else None,
            abc.abstractmethod(obj.fset) if obj.fset is not None else None,
            abc.abstractmethod(obj.fdel) if obj.fdel is not None else None,
        ))
    elif isinstance(obj, (classmethod, staticmethod)):
        return ta.cast(T, type(obj)(abc.abstractmethod(obj.__func__)))
    else:
        return obj


class AbstractTypeError(TypeError):
    pass


class Abstract(abc.ABC):  # noqa
    __slots__ = ()

    def __forceabstract__(self):
        raise TypeError

    setattr(__forceabstract__, _IS_ABSTRACT_METHOD_ATTR, True)

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        if Abstract in cls.__bases__:
            setattr(cls, _FORCE_ABSTRACT_ATTR, getattr(Abstract, _FORCE_ABSTRACT_ATTR))
        else:
            setattr(cls, _FORCE_ABSTRACT_ATTR, False)

        super().__init_subclass__(**kwargs)

        if not _DISABLE_CHECKS and Abstract not in cls.__bases__:
            ams = {a for a, o in cls.__dict__.items() if is_abstract_method(o)}
            seen = set(cls.__dict__)
            for b in cls.__bases__:
                ams.update(set(getattr(b, _ABSTRACT_METHODS_ATTR, [])) - seen)
                seen.update(dir(b))
            if ams:
                raise AbstractTypeError(
                    f'Cannot subclass abstract class {cls.__name__} with abstract methods: '
                    f'{", ".join(map(str, sorted(ams)))}',
                )


def is_abstract_method(obj: ta.Any) -> bool:
    return bool(getattr(obj, _IS_ABSTRACT_METHOD_ATTR, False))


def is_abstract_class(obj: ta.Any) -> bool:
    if bool(getattr(obj, _ABSTRACT_METHODS_ATTR, [])):
        return True
    if isinstance(obj, type):
        if Abstract in obj.__bases__:
            return True
        if (
                Abstract in obj.__mro__
                and getattr(obj.__dict__.get(_FORCE_ABSTRACT_ATTR, None), _IS_ABSTRACT_METHOD_ATTR, False)
        ):
            return True
    return False


def is_abstract(obj: ta.Any) -> bool:
    return is_abstract_method(obj) or is_abstract_class(obj)


def get_abstract_methods(cls: type, *, include_internal: bool = False) -> frozenset[str]:
    ms = frozenset(getattr(cls, _ABSTRACT_METHODS_ATTR))
    if not include_internal:
        ms -= _INTERNAL_ABSTRACT_ATTRS
    return ms


def unabstract_class(
        members: ta.Iterable[str | tuple[str, ta.Any]],
):  # -> ta.Callable[[type[T]], type[T]]:
    def inner(cls):
        if isinstance(members, str):
            raise TypeError(members)

        ams = getattr(cls, _ABSTRACT_METHODS_ATTR)

        names: set[str] = set()
        for m in members:
            if isinstance(m, str):
                if m not in ams:
                    raise NameError(m)
                getattr(cls, m)
                names.add(m)

            elif isinstance(m, tuple):
                name, impl = m
                if name not in ams:
                    raise NameError(name)
                if isinstance(impl, str):
                    impl = getattr(cls, impl)
                setattr(cls, name, impl)
                names.add(name)

        setattr(cls, _ABSTRACT_METHODS_ATTR, ams - names)
        return cls

    return inner
