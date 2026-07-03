from .. import lang
from .core.symbols import TypeInfo
from .core.typekeys import Type
from .core.types import TypeVarLikeType
from .mirror import Mirror
from .mirror import MirrorImpl


##


@lang.cached_function(lock=True)
def global_mirror() -> Mirror:
    return MirrorImpl()


def or_global_mirror(mirror: Mirror | None) -> Mirror:
    return mirror if mirror is not None else global_mirror()


##
# universe


def get_runtime_type(info: TypeInfo, *, mirror: Mirror | None = None) -> object | None:
    return or_global_mirror(mirror).get_runtime_type(info)


def get_type_info(obj: type | str, *, mirror: Mirror | None = None) -> TypeInfo:
    return or_global_mirror(mirror).get_type_info(obj)


def get_newtype_info(obj: object, *, mirror: Mirror | None = None) -> TypeInfo:
    return or_global_mirror(mirror).get_newtype_info(obj)


##
# mirror


def resolve_runtime_type_param(typ: TypeVarLikeType, *, mirror: Mirror | None = None) -> object | None:
    return or_global_mirror(mirror).resolve_runtime_type_param(typ)


def reflect_type(obj: object, *, mirror: Mirror | None = None) -> Type:
    return or_global_mirror(mirror).reflect_type(obj)
