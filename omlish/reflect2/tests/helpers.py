import threading
import typing as ta

from ..interning import Interner
from ..reflector import TypeReflector
from ..universe import TypeUniverse


def make_reflector(
        universe: TypeUniverse | None = None,
        **kwargs: ta.Any,
) -> TypeReflector:
    return TypeReflector(
        universe=universe or TypeUniverse(),
        lock=(lock := threading.RLock()),
        interner=Interner(lock=lock),
        **kwargs,
    )
