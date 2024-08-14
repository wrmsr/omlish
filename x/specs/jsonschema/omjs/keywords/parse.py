import operator
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import lang

from . import core as _  # noqa
from . import metadata as _  # noqa
from . import validation as _  # noqa
from .base import BooleanKeyword
from .base import Keyword
from .base import Keywords
from .base import KeywordsKeyword
from .base import NumberKeyword
from .base import StrKeyword
from .base import StrOrStrsKeyword
from .base import StrToKeywordsKeyword


KeywordT = ta.TypeVar('KeywordT', bound=Keyword)


##


KEYWORD_TYPES_BY_TAG: ta.Mapping[str, type[Keyword]] = col.unique_map_by(  # type: ignore
    operator.attrgetter('tag'),
    (cls for cls in lang.deep_subclasses(Keyword) if not lang.is_abstract_class(cls)),
    strict=True,
)


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
