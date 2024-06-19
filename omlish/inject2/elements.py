import typing as ta

from .. import check
from .. import collections as col
from .. import dataclasses as dc
from .. import lang


class Element(lang.Abstract):
    pass


@dc.dataclass(frozen=True, eq=False)
class Elements(lang.Final):
    es: ta.Sequence[Element] | None = dc.xfield(default=None, coerce=col.optional_seq_of(check.of_isinstance(Element)))
    cs: ta.Sequence['Elements'] | None = dc.xfield(default=None, coerce=col.optional_seq_of(lambda e: check.isinstance(e, Elements)))  # noqa

    def __iter__(self) -> ta.Generator[Element, None, None]:
        if self.es:
            yield from self.es
        if self.cs:
            for c in self.cs:
                yield from c
