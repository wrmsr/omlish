import operator
import typing as ta

from .... import check
from .... import collections as col
from .... import lang
from .base import BooleanKeyword
from .base import Keyword
from .base import Keywords
from .base import KeywordsKeyword
from .base import NumberKeyword
from .base import StrKeyword
from .base import StrOrStrsKeyword
from .base import StrToKeywordsKeyword
from .core import CoreKeyword
from .metadata import MetadataKeyword
from .validation import ValidationKeyword


KeywordT = ta.TypeVar('KeywordT', bound=Keyword)


##


def build_keyword_types_by_tag(keyword_types: ta.Iterable[type[Keyword]]) -> ta.Mapping[str, type[Keyword]]:
    return col.make_map_by(operator.attrgetter('tag'), keyword_types, strict=True)


DEFAULT_KEYWORD_SUPERTYPES: ta.AbstractSet = frozenset([
    CoreKeyword,
    MetadataKeyword,
    ValidationKeyword,
])

DEFAULT_KEYWORD_TYPES: ta.AbstractSet = frozenset(lang.flatten(
    lang.deep_subclasses(st, concrete_only=True) for st in DEFAULT_KEYWORD_SUPERTYPES
))

DEFAULT_KEYWORD_TYPES_BY_TAG: ta.Mapping[str, type[Keyword]] = build_keyword_types_by_tag(DEFAULT_KEYWORD_TYPES)


##


class Parser:
    def __init__(
            self,
            keyword_types: ta.Iterable[type[Keyword]] | ta.Mapping[str, type[Keyword]] = DEFAULT_KEYWORD_TYPES_BY_TAG,
    ) -> None:
        super().__init__()

        if isinstance(keyword_types, ta.Mapping):
            self._keyword_types_by_tag = keyword_types
        else:
            self._keyword_types_by_tag = build_keyword_types_by_tag(keyword_types)

    def parse_keyword(self, cls: type[KeywordT], v: ta.Any) -> KeywordT:
        if issubclass(cls, BooleanKeyword):
            return cls(check.isinstance(v, bool))  # type: ignore

        elif issubclass(cls, NumberKeyword):
            return cls(check.isinstance(v, (int, float)))  # type: ignore

        elif issubclass(cls, StrKeyword):
            return cls(check.isinstance(v, str))  # type: ignore

        elif issubclass(cls, StrOrStrsKeyword):
            ss: str | ta.Sequence[str]
            if isinstance(v, str):
                ss = v
            elif isinstance(v, ta.Iterable):
                ss = col.seq_of(check.of_isinstance(str))(v)
            else:
                raise TypeError(v)
            return cls(ss)  # type: ignore

        elif issubclass(cls, KeywordsKeyword):
            return cls(parse_keywords(v))  # type: ignore

        elif issubclass(cls, StrToKeywordsKeyword):
            return cls({k: parse_keywords(mv) for k, mv in v.items()})  # type: ignore

        else:
            raise TypeError(cls)

    def parse_keywords(self, dct: ta.Mapping[str, ta.Any]) -> Keywords:
        lst: list[Keyword] = []
        for k, v in dct.items():
            cls = self._keyword_types_by_tag[k]
            lst.append(self.parse_keyword(cls, v))
        return Keywords(lst)


##


DEFAULT_PARSER = Parser()

parse_keyword = DEFAULT_PARSER.parse_keyword
parse_keywords = DEFAULT_PARSER.parse_keywords
