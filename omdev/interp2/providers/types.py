import dataclasses as dc
import typing as ta

from ...amalg.std.versions.versions import Version
from ...amalg.std.versions.versions import parse_version


INTERP_OPT_GLYPHS: ta.Mapping[str, str] = {
    'threaded': 't',
    'debug': 'd',
}


@dc.dataclass(frozen=True)
class InterpOpts:
    threaded: bool = False
    debug: bool = False

    def __str__(self) -> str:
        return ''.join(g for a, g in INTERP_OPT_GLYPHS.items() if getattr(self, a))

    @classmethod
    def parse(cls, s: str) -> 'InterpOpts':
        kw = {}
        for g in s:
            kw[INTERP_OPT_GLYPHS[g]] = True
        return cls(**kw)


@dc.dataclass(frozen=True)
class InterpVersion:
    version: Version
    opts: InterpOpts

    def __str__(self) -> str:
        s = str(self.version)
        if (gs := str(self.opts)):
            s += ',' + gs
        return s

    @classmethod
    def parse(cls, s: str) -> 'InterpVersion':
        if ',' in s:
            v, o = s.split(',')
        else:
            v, o = s, ''
        return cls(
            version=parse_version(v),
            opts=InterpOpts.parse(o),
        )


@dc.dataclass(frozen=True)
class Interp:
    exe: str
    provider: str
    version: InterpVersion
