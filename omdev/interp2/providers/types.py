import dataclasses as dc

from ...amalg.std.versions.versions import Version


@dc.dataclass(frozen=True)
class InterpOpts:
    debug: bool = False
    threaded: bool = False


@dc.dataclass(frozen=True)
class InterpVersion:
    version: Version
    opts: InterpOpts


@dc.dataclass(frozen=True)
class Interp:
    exe: str
    provider: str
    version: InterpVersion
