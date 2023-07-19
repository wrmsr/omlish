import dataclasses as dc
import enum
import types


HAS_DEFAULT_FACTORY = dc._HAS_DEFAULT_FACTORY  # noqa


def _patch_missing_ctor():
    # dc.asdict uses copy.deepcopy which instantiates new _MISSING_TYPE objects which do not pass the 'foo is MISSING'
    # checks used throughout dataclasses code. Code should not depend on this behavior but it is a debugging landmine.
    if dc._MISSING_TYPE.__new__ is object.__new__:  # noqa
        def _MISSING_TYPE_new(cls):  # noqa
            return dc.MISSING
        dc._MISSING_TYPE.__new__ = _MISSING_TYPE_new  # type: ignore  # noqa


class FieldType(enum.Enum):
    INSTANCE = dc._FIELD  # type: ignore  # noqa
    CLASS = dc._FIELD_CLASSVAR  # type: ignore  # noqa
    INIT = dc._FIELD_INITVAR  # type: ignore  # noqa


FIELDS_ATTR = dc._FIELDS  # type: ignore  # noqa
PARAMS_ATTR = dc._PARAMS  # type: ignore  # noqa

POST_INIT_NAME = dc._POST_INIT_NAME  # type: ignore  # noqa


def get_field_type(fld: dc.Field) -> FieldType:
    return fld._field_type  # type: ignore  # noqa


DataclassParams = dc._DataclassParams  # type: ignore  # noqa


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


recursive_repr = dc._recursive_repr  # type: ignore  # noqa
tuple_str = dc._tuple_str  # type: ignore  # noqa
HASH_ACTIONS = dc._hash_action  # type: ignore  # noqa
is_dataclass_instance = dc._is_dataclass_instance  # type: ignore  # noqa
