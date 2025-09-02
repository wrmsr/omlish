# ruff: noqa: UP006
import functools
import typing as ta


##


_ANNOTATION_ATTRS: ta.FrozenSet[str] = frozenset([
    '__annotations__',

    '__annotate__',
    '__annotate_func__',

    '__annotations_cache__',
])

_UPDATE_WRAPPER_ASSIGNMENTS_NO_ANNOTATIONS: ta.Sequence[str] = list(frozenset(functools.WRAPPER_ASSIGNMENTS) - _ANNOTATION_ATTRS)  # noqa


def update_wrapper_no_annotations(wrapper, wrapped):
    functools.update_wrapper(wrapper, wrapped, assigned=_UPDATE_WRAPPER_ASSIGNMENTS_NO_ANNOTATIONS)
    return wrapper
