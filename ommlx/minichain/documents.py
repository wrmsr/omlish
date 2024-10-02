import typing as ta

from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True)
class Metadata(lang.Final):
    dct: ta.Mapping[ta.Any, ta.Any] = col.frozendict()


@dc.dataclass(frozen=True)
class TextSegment(lang.Final):
    s: str
    md: Metadata = Metadata()


# @dc.dataclass(frozen=True)
# class Document:
#     ...
