"""
For arcane import machinery compatibility with stdlib, this must be a direct child of the 'dataclasses' package - not
under 'impl'.
"""
import dataclasses as dc
import enum
import sys
import types
import typing as ta


##


STD_HAS_DEFAULT_FACTORY = dc._HAS_DEFAULT_FACTORY  # type: ignore  # noqa

STD_FIELDS_ATTR = dc._FIELDS  # type: ignore  # noqa
STD_PARAMS_ATTR = dc._PARAMS  # type: ignore  # noqa

STD_POST_INIT_NAME = dc._POST_INIT_NAME  # type: ignore  # noqa

StdParams = dc._DataclassParams  # type: ignore  # noqa


##


std_is_dataclass_instance = dc._is_dataclass_instance  # type: ignore  # noqa


##


STD_ATOMIC_TYPES: frozenset[type]

if hasattr(dc, '_ATOMIC_TYPES'):
    STD_ATOMIC_TYPES = getattr(dc, '_ATOMIC_TYPES')

else:
    STD_ATOMIC_TYPES = frozenset({
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


class StdFieldType(enum.Enum):
    INSTANCE = dc._FIELD  # type: ignore  # noqa
    CLASS_VAR = dc._FIELD_CLASSVAR  # type: ignore  # noqa
    INIT_VAR = dc._FIELD_INITVAR  # type: ignore  # noqa


STD_FIELD_TYPE_MAP: ta.Mapping[ta.Any, StdFieldType] = {v.value: v for v in StdFieldType}


def std_field_type(f: dc.Field) -> StdFieldType:
    if (ft := getattr(f, '_field_type')) is not None:
        return STD_FIELD_TYPE_MAP[ft]
    else:
        return StdFieldType.INSTANCE


##


_SELF_MODULE = None


def _self_module():
    global _SELF_MODULE
    if _SELF_MODULE is None:
        _SELF_MODULE = sys.modules[__package__]
    return _SELF_MODULE


def std_is_classvar(cls: type, ty: ta.Any) -> bool:
    return (
        dc._is_classvar(ty, ta)  # type: ignore  # noqa
        or (
            isinstance(ty, str) and
            dc._is_type(ty, cls, ta, ta.ClassVar, dc._is_classvar)  # type: ignore  # noqa
        )
    )


def std_is_initvar(cls: type, ty: ta.Any) -> bool:
    return (
        dc._is_initvar(ty, dc)  # type: ignore  # noqa
        or (
            isinstance(ty, str) and
            any(
                dc._is_type(ty, cls, mod, dc.InitVar, dc._is_initvar)  # type: ignore  # noqa
                for mod in (dc, _self_module())
            )
        )
    )


def std_is_kw_only(cls: type, ty: ta.Any) -> bool:
    return (
        dc._is_kw_only(ty, dc)  # type: ignore  # noqa
        or (
            isinstance(ty, str) and
            any(
                dc._is_type(ty, cls, mod, dc.KW_ONLY, dc._is_kw_only)  # type: ignore  # noqa
                for mod in (dc, _self_module())
            )
        )
    )
