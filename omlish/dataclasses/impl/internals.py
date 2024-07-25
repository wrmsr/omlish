import dataclasses as dc
import enum
import sys
import types
import typing as ta


##


HAS_DEFAULT_FACTORY = dc._HAS_DEFAULT_FACTORY  # type: ignore  # noqa

FIELDS_ATTR = dc._FIELDS  # type: ignore  # noqa
PARAMS_ATTR = dc._PARAMS  # type: ignore  # noqa

POST_INIT_NAME = dc._POST_INIT_NAME  # type: ignore  # noqa

Params = dc._DataclassParams  # type: ignore  # noqa

"""
@dc.dataclass(frozen=True)
class Params:
    init = True
    repr = True
    eq = True
    order = False
    unsafe_hash = False
    frozen = False
    match_args = True
    kw_only = False
    slots = False
    weakref_slot = False
"""


##


is_dataclass_instance = dc._is_dataclass_instance  # type: ignore  # noqa


##


ATOMIC_TYPES: frozenset[type]

if hasattr(dc, '_ATOMIC_TYPES'):
    ATOMIC_TYPES = getattr(dc, '_ATOMIC_TYPES')

else:
    ATOMIC_TYPES = frozenset({
        types.NoneType,
        bool,
        int,
        float,
        str,

        complex,
        bytes,

        types.EllipsisType,
        types.NotImplementedType,
        types.CodeType,
        types.BuiltinFunctionType,
        types.FunctionType,
        type,
        range,
        property,
    })


##


def _patch_missing_ctor() -> None:
    # dc.asdict uses copy.deepcopy which instantiates new _MISSING_TYPE objects which do not pass the 'foo is MISSING'
    # checks used throughout dataclasses code. Code should not depend on this behavior but it is a debugging landmine.
    if dc._MISSING_TYPE.__new__ is object.__new__:  # noqa
        def _MISSING_TYPE_new(cls):  # noqa
            return dc.MISSING
        dc._MISSING_TYPE.__new__ = _MISSING_TYPE_new  # type: ignore  # noqa


##


class FieldType(enum.Enum):
    INSTANCE = dc._FIELD  # type: ignore  # noqa
    CLASS = dc._FIELD_CLASSVAR  # type: ignore  # noqa
    INIT = dc._FIELD_INITVAR  # type: ignore  # noqa


_SELF_MODULE = None


def _self_module():
    global _SELF_MODULE
    if _SELF_MODULE is None:
        _SELF_MODULE = sys.modules[__package__.rpartition('.')[0]]
    return _SELF_MODULE


def is_classvar(cls: type, ty: ta.Any) -> bool:
    return (
        dc._is_classvar(ty, ta)  # type: ignore  # noqa
        or (isinstance(ty, str) and dc._is_type(ty, cls, ta, ta.ClassVar, dc._is_classvar))  # type: ignore  # noqa
    )


def is_initvar(cls: type, ty: ta.Any) -> bool:
    return (
        dc._is_initvar(ty, dc)  # type: ignore  # noqa
        or (
            isinstance(ty, str)
            and any(
                dc._is_type(ty, cls, mod, dc.InitVar, dc._is_initvar)  # type: ignore  # noqa
                for mod in (dc, _self_module())
            )
        )
    )


def is_kw_only(cls: type, ty: ta.Any) -> bool:
    return (
        dc._is_kw_only(ty, dc)  # type: ignore  # noqa
        or (
            isinstance(ty, str)
            and any(
                dc._is_type(ty, cls, mod, dc.KW_ONLY, dc._is_kw_only)  # type: ignore  # noqa
                for mod in (dc, _self_module())
            )
        )
    )
