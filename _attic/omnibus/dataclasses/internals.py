import dataclasses as dc

from .. import lang


def _patch_missing_ctor():
    # dc.asdict uses copy.deepcopy which instantiates new _MISSING_TYPE objects which do not pass the 'foo is MISSING'
    # checks used throughout dataclasses code. Code should not depend on this behavior but it is a debugging landmine.
    def _MISSING_TYPE_new(cls):
        return dc.MISSING
    dc._MISSING_TYPE.__new__ = _MISSING_TYPE_new  # type: ignore


FIELDS = dc._FIELDS  # type: ignore
PARAMS = dc._PARAMS  # type: ignore

POST_INIT_NAME = dc._POST_INIT_NAME  # type: ignore


class FieldType(lang.ValueEnum):
    INSTANCE = dc._FIELD  # type: ignore
    CLASS = dc._FIELD_CLASSVAR  # type: ignore
    INIT = dc._FIELD_INITVAR  # type: ignore


def get_field_type(fld: dc.Field) -> FieldType:
    return fld._field_type  # type: ignore


DataclassParams = dc._DataclassParams  # type: ignore


tuple_str = dc._tuple_str  # type: ignore
recursive_repr = dc._recursive_repr  # type: ignore
get_field = dc._get_field  # type: ignore
hash_action = dc._hash_action  # type: ignore
is_dataclass_instance = dc._is_dataclass_instance  # type: ignore
