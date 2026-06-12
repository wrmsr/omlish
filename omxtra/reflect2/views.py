import dataclasses as dc

from .core.types import Type
from .queries import RuntimeCollectionShape
from .queries import RuntimeDispatch
from .queries import RuntimeMappingShape
from .queries import RuntimeTypeKeys
from .queries import RuntimeTypeShape
from .queries import get_runtime_collection_shape
from .queries import get_runtime_dispatch
from .queries import get_runtime_mapping_shape
from .queries import get_runtime_type_keys
from .queries import get_runtime_type_shape
from .reflect import DEFAULT_REFLECTOR
from .reflect import RuntimeTypeReflector


##


@dc.dataclass(frozen=True)
class RuntimeTypeView:
    typ: Type
    shape: RuntimeTypeShape
    collection: RuntimeCollectionShape
    mapping: RuntimeMappingShape | None
    dispatch: RuntimeDispatch
    keys: RuntimeTypeKeys


##


def _get_reflector(reflector: RuntimeTypeReflector | None) -> RuntimeTypeReflector:
    return DEFAULT_REFLECTOR if reflector is None else reflector


def get_runtime_type_view(
        typ: Type,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeTypeView:
    rt_reflector = _get_reflector(reflector)
    return RuntimeTypeView(
        typ,
        get_runtime_type_shape(typ, rt_reflector),
        get_runtime_collection_shape(typ, rt_reflector),
        get_runtime_mapping_shape(typ, rt_reflector),
        get_runtime_dispatch(typ, rt_reflector),
        get_runtime_type_keys(typ, rt_reflector),
    )


def reflect_runtime_type_view(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeTypeView:
    rt_reflector = _get_reflector(reflector)
    return get_runtime_type_view(rt_reflector.reflect_type(obj), rt_reflector)
