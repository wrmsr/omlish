import abc
import dataclasses as dc
import enum
import typing as ta

from omlish import collections as col
from omlish import lang


##




@dc.dataclass(frozen=True)
class JsonSchema(lang.Final):
    name: str
    root: ta.Any


##


class ResponseFormat(lang.Abstract, lang.Sealed):
    pass


class TextResponseFormat(ResponseFormat, lang.Final):
    pass


class JsonResponseFormat(lang.Final):
    schema: JsonSchema | None = None




##


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

