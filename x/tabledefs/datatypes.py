from omlish import dataclasses as dc
from omlish import lang


@dc.dataclass(frozen=True)
class Datatype(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class Integer(Datatype, lang.Singleton):
    pass


@dc.dataclass(frozen=True)
class String(Datatype, lang.Singleton):
    pass


@dc.dataclass(frozen=True)
class Datetime(Datatype, lang.Singleton):
    pass
