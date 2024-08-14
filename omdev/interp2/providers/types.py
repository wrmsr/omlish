import collections
import dataclasses as dc
import typing as ta

from ...amalg.std.versions.specifiers import Specifier
from ...amalg.std.versions.versions import InvalidVersion
from ...amalg.std.versions.versions import Version


# See https://peps.python.org/pep-3149/
INTERP_OPT_GLYPHS: ta.Mapping[str, str] = collections.OrderedDict([
    ('debug', 'd'),
    ('threaded', 't'),
])


@dc.dataclass(frozen=True)
class InterpOpts:
    threaded: bool = False
    debug: bool = False

    def __str__(self) -> str:
        return ''.join(g for a, g in INTERP_OPT_GLYPHS.items() if getattr(self, a))

    @classmethod
    def parse(cls, s: str) -> 'InterpOpts':
        return cls(**{INTERP_OPT_GLYPHS[g]: True for g in s})

    @classmethod
    def parse_suffix(cls, s: str) -> ta.Tuple[str, 'InterpOpts']:
        kw = {}
        while s and (a := INTERP_OPT_GLYPHS.get(s[-1])):
            s, kw[a] = s[:-1], True
        return s, cls(**kw)


@dc.dataclass(frozen=True)
class InterpVersion:
    version: Version
    opts: InterpOpts

    def __str__(self) -> str:
        return ''.join([str(self.version), *(() if not (gs := str(self.opts)) else [gs])])

    @classmethod
    def parse(cls, s: str) -> 'InterpVersion':
        s, o = InterpOpts.parse_suffix(s)
        v = Version(s)
        return cls(
            version=v,
            opts=o,
        )

    @classmethod
    def try_parse(cls, s: str) -> ta.Optional['InterpVersion']:
        try:
            return cls.parse(s)
        except (KeyError, InvalidVersion):
            return None


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
