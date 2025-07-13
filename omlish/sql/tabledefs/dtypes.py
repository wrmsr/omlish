from ... import dataclasses as dc
from ... import lang


##


@dc.dataclass(frozen=True)
class Dtype(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class Integer(Dtype, lang.Singleton):
    pass


@dc.dataclass(frozen=True)
class String(Dtype, lang.Singleton):
    pass


@dc.dataclass(frozen=True)
class Datetime(Dtype, lang.Singleton):
    pass
