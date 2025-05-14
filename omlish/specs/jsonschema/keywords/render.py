import typing as ta

from .base import AnyArrayKeyword
from .base import AnyKeyword
from .base import BooleanKeyword
from .base import BooleanOrKeywordsKeyword
from .base import Keyword
from .base import Keywords
from .base import KeywordsArrayKeyword
from .base import KeywordsKeyword
from .base import NumberKeyword
from .base import StrKeyword
from .base import StrOrStrArrayKeyword
from .base import StrToKeywordsKeyword
from .base import UnknownKeyword


##


def render_keyword(kw: Keyword) -> dict[str, ta.Any]:
    if isinstance(kw, AnyKeyword):
        return {kw.tag: kw.v}

    elif isinstance(kw, AnyArrayKeyword):
        return {kw.tag: kw.vs}

    elif isinstance(kw, BooleanKeyword):
        return {kw.tag: kw.b}

    elif isinstance(kw, BooleanOrKeywordsKeyword):
        if isinstance(kw.bk, bool):
            return {kw.tag: kw.bk}
        else:
            return {kw.tag: render_keywords(kw.bk)}

    elif isinstance(kw, NumberKeyword):
        return {kw.tag: kw.n}

    elif isinstance(kw, StrKeyword):
        return {kw.tag: kw.s}

    elif isinstance(kw, StrOrStrArrayKeyword):
        if isinstance(kw.ss, str):
            return {kw.tag: kw.ss}
        else:
            return {kw.tag: list(kw.ss)}

    elif isinstance(kw, KeywordsKeyword):
        return {kw.tag: render_keywords(kw.kw)}

    elif isinstance(kw, KeywordsArrayKeyword):
        return {kw.tag: [render_keywords(c) for c in kw.kws]}

    elif isinstance(kw, StrToKeywordsKeyword):
        return {kw.tag: {k: render_keywords(v) for k, v in kw.m.items()}}

    elif isinstance(kw, UnknownKeyword):
        return {kw.tag: kw.value}

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
