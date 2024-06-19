import typing as ta

from .elements import Element
from .elements import Elements


def bind(*args: ta.Any) -> Elements:
    if all(isinstance(a, (Element, Elements)) for a in args):
        es = [a for a in args if isinstance(a, Element)]
        cs = [a for a in args if isinstance(a, Elements)]
        return Elements(es, cs)

    raise TypeError(args)
