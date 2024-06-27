"""
TODO:
 - as_element[s] - universal
"""
import typing as ta

from .. import dataclasses as dc
from .. import lang


class Element(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Elements(lang.Final):
    es: frozenset[Element] | None = None
    cs: frozenset['Elements'] | None = None

    def __iter__(self) -> ta.Generator[Element, None, None]:
        if self.es:
            yield from self.es
        if self.cs:
            for c in self.cs:
                yield from c


def as_elements(*args: ta.Union[Element, Elements]) -> Elements:
    es: set[Element] = set()
    cs: set['Elements'] = set()
    for a in args:
        if isinstance(a, Element):
            es.add(a)
        elif isinstance(a, Elements):
            cs.add(a)
        else:
            raise TypeError(a)
    if not es and len(cs) == 1:
        return next(iter(cs))
    return Elements(
        frozenset(es) if es else None,
        frozenset(cs) if cs else None,
    )
