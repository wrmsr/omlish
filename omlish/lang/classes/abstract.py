import abc
import typing as ta

from ...lite.abstract import _ABSTRACT_METHODS_ATTR  # noqa
from ...lite.abstract import _FORCE_ABSTRACT_ATTR  # noqa
from ...lite.abstract import _IS_ABSTRACT_METHOD_ATTR  # noqa
from ...lite.abstract import Abstract
from ...lite.abstract import is_abstract_method


T = ta.TypeVar('T')


##


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


##


_INTERNAL_ABSTRACT_ATTRS = frozenset([_FORCE_ABSTRACT_ATTR])


def get_abstracts(cls: type, *, include_internal: bool = False) -> frozenset[str]:
    ms = frozenset(getattr(cls, _ABSTRACT_METHODS_ATTR))
    if not include_internal:
        ms -= _INTERNAL_ABSTRACT_ATTRS
    return ms


##


def make_abstract(obj: T) -> T:
    if callable(obj):
        return abc.abstractmethod(obj)

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
