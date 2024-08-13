"""
TODO:
 - reflecty generalized rewriter, obviously..
 - env vars
 - coalescing - {$FOO|$BAR|baz}
"""
import collections.abc
import typing as ta

from .. import dataclasses as dc
from .. import lang
from ..text import glyphsplit


T = ta.TypeVar('T')


class InterpolateStringsMetadata(lang.Marker):
    pass


@dc.field_modifier
def secret_or_key_field(f: dc.Field) -> dc.Field:
    return dc.update_field_metadata(f, {
        InterpolateStringsMetadata: True,
    })


@dc.field_modifier
def interpolate_field(f: dc.Field) -> dc.Field:
    return dc.update_field_metadata(f, {InterpolateStringsMetadata: True})


class StringRewriter:
    def __init__(self, fn: ta.Callable[[str], str]) -> None:
        super().__init__()
        self._fn = fn

    def __call__(self, v: T, *, _soft: bool = False) -> T:
        if v is None:
            return None  # type: ignore

        if dc.is_dataclass(v):
            kw = {}
            for f in dc.fields(v):
                fv = getattr(v, f.name)
                nfv = self(fv, _soft=not f.metadata.get(InterpolateStringsMetadata))
                if fv is not nfv:
                    kw[f.name] = nfv
            if not kw:
                return v  # type: ignore
            return dc.replace(v, **kw)

        if isinstance(v, str):
            if not _soft:
                v = self._fn(v)  # type: ignore
            return v  # type: ignore

        if isinstance(v, lang.BUILTIN_SCALAR_ITERABLE_TYPES):
            return v  # type: ignore

        if isinstance(v, collections.abc.Mapping):
            nm = []
            b = False
            for mk, mv in v.items():
                nk, nv = self(mk, _soft=_soft), self(mv, _soft=_soft)
                nm.append((nk, nv))
                b |= nk is not mk or nv is not mv
            if not b:
                return v  # type: ignore
            return v.__class__(nm)  # type: ignore

        if isinstance(v, (collections.abc.Sequence, collections.abc.Set)):
            nl = []
            b = False
            for le in v:
                ne = self(le, _soft=_soft)
                nl.append(ne)
                b |= ne is not le
            if not b:
                return v  # type: ignore
            return v.__class__(nl)  # type: ignore

        return v


def interpolate_strings(v: T, rpl: ta.Mapping[str, str]) -> T:
    def fn(v):
        if not v:
            return v
        sps = glyphsplit.split_braces(v)
        if len(sps) == 1 and isinstance(sps[0], str):
            return sps[0]
        return ''.join(rpl[p.s] if isinstance(p, glyphsplit.GlyphMatch) else p for p in sps)

    return StringRewriter(fn)(v)
