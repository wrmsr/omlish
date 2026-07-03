from .. import lang
from .core.symbols import TypeInfo
from .core.typekeys import Type
from .core.types import TypeVarLikeType
from .reflector import TypeReflector
from .reflector import TypeReflectorImpl


##


@lang.cached_function(lock=True)
def global_reflector() -> TypeReflector:
    return TypeReflectorImpl()


def or_global_reflector(reflector: TypeReflector | None) -> TypeReflector:
    return reflector if reflector is not None else global_reflector()


##
# universe


def get_runtime_type(info: TypeInfo, *, reflector: TypeReflector | None = None) -> object | None:
    return or_global_reflector(reflector).get_runtime_type(info)


def get_type_info(obj: type | str, *, reflector: TypeReflector | None = None) -> TypeInfo:
    return or_global_reflector(reflector).get_type_info(obj)


def get_newtype_info(obj: object, *, reflector: TypeReflector | None = None) -> TypeInfo:
    return or_global_reflector(reflector).get_newtype_info(obj)


##
# reflector


def resolve_runtime_type_param(typ: TypeVarLikeType, *, reflector: TypeReflector | None = None) -> object | None:
    return or_global_reflector(reflector).resolve_runtime_type_param(typ)


def reflect_type(obj: object, *, reflector: TypeReflector | None = None) -> Type:
    return or_global_reflector(reflector).reflect_type(obj)
