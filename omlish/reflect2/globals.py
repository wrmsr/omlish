import threading
import typing as ta

from .core.symbols import TypeInfo
from .core.typekeys import Type
from .core.types import TypeVarLikeType
from .mirror import Mirror
from .mirrorimpl import MirrorImpl


##


@ta.final
class _Globals:
    def __init__(self) -> None:
        self._lock = threading.RLock()

    #

    def _make_mirror(self) -> Mirror:
        return MirrorImpl()

    #

    _mirror: Mirror

    def mirror(self) -> Mirror:
        try:
            return self._mirror
        except AttributeError:
            pass

        with self._lock:
            try:
                return self._mirror
            except AttributeError:
                pass

            mirror = self._make_mirror()
            self._mirror = mirror
            return mirror


_GLOBALS = _Globals()


##


def global_mirror() -> Mirror:
    return _GLOBALS.mirror()


def or_global_mirror(mirror: Mirror | None) -> Mirror:
    return mirror if mirror is not None else _GLOBALS.mirror()


##
# universe


def get_type_info(obj: type | str, *, mirror: Mirror | None = None) -> TypeInfo:
    return or_global_mirror(mirror).get_type_info(obj)


def get_newtype_info(obj: object, *, mirror: Mirror | None = None) -> TypeInfo:
    return or_global_mirror(mirror).get_newtype_info(obj)


##
# reflector


def resolve_runtime_type_param(typ: TypeVarLikeType, *, mirror: Mirror | None = None) -> object | None:
    return or_global_mirror(mirror).resolve_runtime_type_param(typ)


def reflect_type(obj: object, *, mirror: Mirror | None = None) -> Type:
    return or_global_mirror(mirror).reflect_type(obj)
