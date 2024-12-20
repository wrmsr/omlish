import abc
import typing as ta

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
    es: ta.Collection[Element] | None = None
    cs: ta.Collection['Elements'] | None = None

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
    es: list[Element] = []
    cs: list[Elements] = []

    def rec(a):
        if isinstance(a, Element):
            es.append(a)
        elif isinstance(a, Elements):
            cs.append(a)
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
        es if es else None,
        cs if cs else None,
    )
