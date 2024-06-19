import typing as ta

from .. import dataclasses as dc
from .. import lang


class Element(lang.Abstract):
    pass


@dc.dataclass(frozen=True, eq=False)
class Elements(lang.Final):
    es: ta.Sequence[Element] | None = None
    cs: ta.Sequence['Elements'] | None = None

    def __iter__(self) -> ta.Generator[Element, None, None]:
        if self.es:
            yield from self.es
        if self.cs:
            for c in self.cs:
                yield from c
