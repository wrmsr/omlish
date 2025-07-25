import typing as ta

from .... import check
from .... import collections as col
from .... import lang
from .base import AnyArrayKeyword
from .base import AnyKeyword
from .base import BooleanKeyword
from .base import BooleanOrKeywordsKeyword
from .base import Keyword
from .base import Keywords
from .base import KeywordsArrayKeyword
from .base import KeywordsKeyword
from .base import KnownKeyword
from .base import NumberKeyword
from .base import StrKeyword
from .base import StrOrStrArrayKeyword
from .base import StrToKeywordsKeyword
from .base import UnknownKeyword
from .core import CoreKeyword
from .format import FormatKeyword
from .metadata import MetadataKeyword
from .validation import ValidationKeyword


KeywordT = ta.TypeVar('KeywordT', bound=Keyword)


##


def build_keyword_types_by_tag(keyword_types: ta.Iterable[type[KnownKeyword]]) -> ta.Mapping[str, type[KnownKeyword]]:
    return col.make_map(((t, kt) for kt in keyword_types for t in kt.tag_and_aliases), strict=True)


DEFAULT_KEYWORD_SUPERTYPES: ta.AbstractSet[type[KnownKeyword]] = frozenset([
    CoreKeyword,
    FormatKeyword,
    MetadataKeyword,
    ValidationKeyword,
])

DEFAULT_KEYWORD_TYPES: ta.AbstractSet[type[KnownKeyword]] = frozenset(lang.flatten(
    lang.deep_subclasses(st, concrete_only=True) for st in DEFAULT_KEYWORD_SUPERTYPES
))

DEFAULT_KEYWORD_TYPES_BY_TAG: ta.Mapping[str, type[KnownKeyword]] = build_keyword_types_by_tag(DEFAULT_KEYWORD_TYPES)


##


class KeywordParser:
    def __init__(
            self,
            *,
            keyword_types: ta.Union[  # noqa
                ta.Iterable[type[KnownKeyword]],
                ta.Mapping[str, type[KnownKeyword]],
                None,
            ] = None,
            allow_unknown: bool = False,
    ) -> None:
        super().__init__()

        if keyword_types is None:
            self._keyword_types_by_tag = DEFAULT_KEYWORD_TYPES_BY_TAG
        elif isinstance(keyword_types, ta.Mapping):
            self._keyword_types_by_tag = keyword_types
        else:
            self._keyword_types_by_tag = build_keyword_types_by_tag(keyword_types)

        self._allow_unknown = allow_unknown

    def parse_keyword(self, cls: type[KeywordT], v: ta.Any) -> KeywordT:
        if issubclass(cls, AnyKeyword):
            return cls(v)

        elif issubclass(cls, AnyArrayKeyword):
            return cls(tuple(check.isinstance(v, ta.Sequence)))

        elif issubclass(cls, BooleanKeyword):
            return cls(check.isinstance(v, bool))

        elif issubclass(cls, BooleanOrKeywordsKeyword):
            if isinstance(v, bool):
                return cls(v)
            else:
                return cls(self.parse_keywords(v))

        elif issubclass(cls, NumberKeyword):
            return cls(check.isinstance(v, (int, float)))

        elif issubclass(cls, StrKeyword):
            return cls(check.isinstance(v, str))

        elif issubclass(cls, StrOrStrArrayKeyword):
            ss: str | ta.Sequence[str]
            if isinstance(v, str):
                ss = v
            elif isinstance(v, ta.Iterable):
                ss = col.seq_of(check.of_isinstance(str))(v)
            else:
                raise TypeError(v)
            return cls(ss)

        elif issubclass(cls, KeywordsKeyword):
            return cls(self.parse_keywords(v))

        elif issubclass(cls, KeywordsArrayKeyword):
            return cls(tuple(self.parse_keywords(e) for e in v))

        elif issubclass(cls, StrToKeywordsKeyword):
            return cls({k: self.parse_keywords(mv) for k, mv in v.items()})

        else:
            raise TypeError(cls)

    def parse_keywords(self, dct: ta.Mapping[str, ta.Any]) -> Keywords:
        lst: list[Keyword] = []

        for k, v in dct.items():
            try:
                cls = self._keyword_types_by_tag[k]

            except KeyError:
                if not self._allow_unknown:
                    raise

                lst.append(UnknownKeyword(k, v))

            else:
                lst.append(self.parse_keyword(cls, v))

        return Keywords(lst)


##


DEFAULT_KEYWORD_PARSER = KeywordParser()

parse_keyword = DEFAULT_KEYWORD_PARSER.parse_keyword
parse_keywords = DEFAULT_KEYWORD_PARSER.parse_keywords
