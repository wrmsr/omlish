import typing as ta

from .elements import Element
from .elements import Elements
from .elements import as_elements


def bind(*args: ta.Any) -> Elements:
    if all(isinstance(a, (Element, Elements)) for a in args):
        return as_elements(*args)

    raise TypeError(args)
