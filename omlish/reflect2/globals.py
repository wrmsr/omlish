import threading
import typing as ta

from .core.symbols import TypeInfo
from .core.typekeys import Type
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


def get_type_info(obj: type | str | ta.NewType, *, mirror: Mirror | None = None) -> TypeInfo:
    return or_global_mirror(mirror).get_type_info(obj)


def can_reflect_type(obj: object, *, mirror: Mirror | None = None) -> bool:
    if isinstance(obj, (Type, type)):
        return True

    return or_global_mirror(mirror).can_reflect_type(obj)


def reflect_type(obj: object, *, mirror: Mirror | None = None) -> Type:
    if isinstance(obj, Type):
        return obj

    return or_global_mirror(mirror).reflect_type(obj)
