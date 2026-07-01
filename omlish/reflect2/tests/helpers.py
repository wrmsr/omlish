import threading
import typing as ta

from ..interning import Interner
from ..reflector import TypeReflector
from ..universe import DynamicTypeNameSuffix
from ..universe import TypeUniverse


def make_reflector(
        *,
        dynamic_type_name_suffix: DynamicTypeNameSuffix | None = None,
        **kwargs: ta.Any,
) -> TypeReflector:
    return TypeReflector(
        universe=TypeUniverse(
            dynamic_type_name_suffix=dynamic_type_name_suffix,
            lock=(lock := threading.RLock()),
        ),
        interner=Interner(
            lock=lock,
        ),
        lock=lock,
        **kwargs,
    )
