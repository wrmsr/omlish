import typing as ta

from .base import BooleanKeyword
from .base import Keyword
from .base import Keywords
from .base import KeywordsKeyword
from .base import NumberKeyword
from .base import StrKeyword
from .base import StrOrStrsKeyword
from .base import StrToKeywordsKeyword


def render_keyword(kw: Keyword) -> dict[str, ta.Any]:
    if isinstance(kw, BooleanKeyword):
        return {kw.tag: kw.b}

    elif isinstance(kw, NumberKeyword):
        return {kw.tag: kw.n}

    elif isinstance(kw, StrKeyword):
        return {kw.tag: kw.s}

    elif isinstance(kw, StrOrStrsKeyword):
        if isinstance(kw.ss, str):
            return {kw.tag: kw.ss}
        else:
            return {kw.tag: list(kw.ss)}

    elif isinstance(kw, KeywordsKeyword):
        return {kw.tag: render_keywords(kw.kw)}

    elif isinstance(kw, StrToKeywordsKeyword):
        return {kw.tag: {k: render_keywords(v) for k, v in kw.m.items()}}

    else:
        raise TypeError(kw)


def render_keywords(kws: Keywords) -> dict[str, ta.Any]:
    dct: dict[str, ta.Any] = {}
    for kw in kws.lst:
        kwd = render_keyword(kw)
        [(tag, val)] = kwd.items()
        if tag in dct:
            raise KeyError(tag)
        dct[tag] = val
    return dct
