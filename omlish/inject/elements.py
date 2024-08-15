import abc
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .impl.origins import HasOriginsImpl


class Element(HasOriginsImpl, lang.Abstract, lang.PackageSealed):
    """Note: inheritors must be dataclasses."""


class ElementGenerator(lang.Abstract, lang.PackageSealed):
    @abc.abstractmethod
    def __iter__(self) -> ta.Iterator[Element]:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class Elements(lang.Final):
    es: frozenset[Element] | None = dc.xfield(None, coerce=check.of_isinstance((frozenset, None)))
    cs: frozenset['Elements'] | None = dc.xfield(None, coerce=check.of_isinstance((frozenset, None)))

    def __iter__(self) -> ta.Generator[Element, None, None]:
        if self.es:
            yield from self.es
        if self.cs:
            for c in self.cs:
                yield from c


Elemental = ta.Union[  # noqa
    Element,
    Elements,
    ElementGenerator,
]


def as_elements(*args: Elemental) -> Elements:
    es: set[Element] = set()
    cs: set[Elements] = set()

    def rec(a):
        if isinstance(a, Element):
            es.add(a)
        elif isinstance(a, Elements):
            cs.add(a)
        elif isinstance(a, ElementGenerator):
            for n in a:
                rec(n)
        else:
            raise TypeError(a)

    for a in args:
        rec(a)

    if not es and len(cs) == 1:
        return next(iter(cs))

    return Elements(
        frozenset(es) if es else None,
        frozenset(cs) if cs else None,
    )
