import typing as ta

from omlish import check
from omlish import collections as col

from .keywords import BooleanKeyword
from .keywords import KEYWORD_TYPES_BY_TAG
from .keywords import Keyword
from .keywords import Keywords
from .keywords import KeywordsKeyword
from .keywords import NumberKeyword
from .keywords import StrKeyword
from .keywords import StrOrStrsKeyword
from .keywords import StrToKeywordsKeyword


KeywordT = ta.TypeVar('KeywordT', bound=Keyword)


def parse_keyword(cls: type[KeywordT], v: ta.Any) -> KeywordT:
    if issubclass(cls, BooleanKeyword):
        return cls(check.isinstance(v, bool))

    elif issubclass(cls, NumberKeyword):
        return cls(check.isinstance(v, (int, float)))

    elif issubclass(cls, StrKeyword):
        return cls(check.isinstance(v, str))

    elif issubclass(cls, StrOrStrsKeyword):
        ss: str | ta.Sequence[str]
        if isinstance(v, str):
            ss = v
        elif isinstance(v, ta.Iterable):
            ss = col.seq_of(check.of_isinstance(str))(v)
        else:
            raise TypeError(v)
        return cls(ss)

    elif issubclass(cls, KeywordsKeyword):
        return cls(parse_keywords(v))

    elif issubclass(cls, StrToKeywordsKeyword):
        return cls({k: parse_keywords(mv) for k, mv in v.items()})

    else:
        raise TypeError(cls)


def parse_keywords(dct: ta.Mapping[str, ta.Any]) -> Keywords:
    lst: list[Keyword] = []
    for k, v in dct.items():
        cls = KEYWORD_TYPES_BY_TAG[k]
        lst.append(parse_keyword(cls, v))
    return Keywords(lst)
