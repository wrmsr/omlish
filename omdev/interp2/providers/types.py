import dataclasses as dc
import typing as ta

from ...amalg.std.versions.specifiers import Specifier
from ...amalg.std.versions.versions import Version


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
        return cls(**{INTERP_OPT_GLYPHS[g]: True for g in s})


@dc.dataclass(frozen=True)
class InterpVersion:
    version: Version
    opts: InterpOpts

    def __str__(self) -> str:
        return ','.join([str(self.version), *(() if not (gs := str(self.opts)) else [gs])])

    @classmethod
    def parse(cls, s: str) -> 'InterpVersion':
        v, o = s.split(',') if ',' in s else (s, '')
        return cls(
            version=Version(v),
            opts=InterpOpts.parse(o),
        )


@dc.dataclass(frozen=True)
class InterpSpecifier:
    specifier: Specifier
    opts: InterpOpts

    def __str__(self) -> str:
        return ','.join([str(self.specifier), *(() if not (gs := str(self.opts)) else [gs])])

    @classmethod
    def parse(cls, s: str) -> 'InterpSpecifier':
        v, o = s.split(',') if ',' in s else (s, '')
        if not any(v.startswith(o) for o in Specifier.OPERATORS):
            v = '~=' + v
        return cls(
            specifier=Specifier(v),
            opts=InterpOpts.parse(o),
        )


@dc.dataclass(frozen=True)
class Interp:
    exe: str
    provider: str
    version: InterpVersion
