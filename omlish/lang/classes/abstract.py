import abc
import typing as ta


T = ta.TypeVar('T')


_DISABLE_CHECKS = False


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


class Abstract(abc.ABC):  # noqa
    __slots__ = ()

    def __forceabstract__(self):
        raise TypeError

    setattr(__forceabstract__, '__isabstractmethod__', True)

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        if Abstract in cls.__bases__:
            cls.__forceabstract__ = Abstract.__forceabstract__  # type: ignore
        else:
            cls.__forceabstract__ = False  # type: ignore

        super().__init_subclass__(**kwargs)

        if not _DISABLE_CHECKS and Abstract not in cls.__bases__:
            ams = {a for a, o in cls.__dict__.items() if is_abstract_method(o)}
            seen = set(cls.__dict__)
            for b in cls.__bases__:
                ams.update(set(getattr(b, '__abstractmethods__', [])) - seen)
                seen.update(dir(b))
            if ams:
                raise TypeError(
                    f'Cannot subclass abstract class {cls.__name__} with abstract methods: '
                    f'{", ".join(map(str, sorted(ams)))}',
                )


def is_abstract_method(obj: ta.Any) -> bool:
    return bool(getattr(obj, '__isabstractmethod__', False))


def is_abstract_class(obj: ta.Any) -> bool:
    if bool(getattr(obj, '__abstractmethods__', [])):
        return True
    if isinstance(obj, type):
        if Abstract in obj.__bases__:
            return True
        if (
                Abstract in obj.__mro__
                and getattr(obj.__dict__.get('__forceabstract__', None), '__isabstractmethod__', False)
        ):
            return True
    return False


def is_abstract(obj: ta.Any) -> bool:
    return is_abstract_method(obj) or is_abstract_class(obj)
