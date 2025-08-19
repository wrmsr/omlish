"""
TODO:
 - vs ta.get_type_hints?
  - eval (ta.get_type_hints) vs forwardref (inspect.get_annotations)?
 - remove, or at least address, get_filtered_type_hints wrt 3.14
"""
import typing as ta

from .. import check
from .. import lang
from ..lite.typing import typing_annotations_attr


if ta.TYPE_CHECKING:
    import inspect
else:
    inspect = lang.proxy_import('inspect')


annotationlib = lang.lazy_import('annotationlib', optional=True, cache_failure=True)


##


def has_annotations(obj: ta.Any) -> bool:
    return hasattr(obj, typing_annotations_attr())


##


def get_annotations(obj: ta.Any) -> ta.Mapping[str, ta.Any]:
    if (al := annotationlib()) is not None:
        return al.get_annotations(obj, format=al.Format.FORWARDREF)  # noqa
    else:
        return inspect.get_annotations(obj)


##


class _TypeHintsTarget:
    def __init__(self, obj, annotations):
        super().__init__()

        self.obj = obj
        self.__annotations__ = annotations
        self.__globals__ = obj.__globals__
        self.__type_params__ = obj.__type_params__


def get_filtered_type_hints(
        obj: ta.Any,
        *,
        include: ta.Container[str] | None = None,
        exclude: ta.Container[str] | None = None,
) -> ta.Mapping[str, ta.Any]:
    """
    Gross hack: get_type_hints doesn't support recursive types, but it's nice to support functions with, at least,
    recursive return types.

    This is consciously constrained in what it supports - basically just functions.
    """

    check.not_isinstance(include, str)
    check.not_isinstance(exclude, str)

    anns = {
        k: v
        for k, v in obj.__annotations__.items()
        if (include is None or k in include)
        and not (exclude is not None and k in exclude)
    }

    return ta.get_type_hints(_TypeHintsTarget(obj, anns))
