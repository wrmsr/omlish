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


@dc.dataclass(frozen=True)
class Uuid(Dtype, lang.Singleton):
    pass


@dc.dataclass(frozen=True)
class Boolean(Dtype, lang.Singleton):
    pass


@dc.dataclass(frozen=True)
class Float(Dtype, lang.Singleton):
    pass


@dc.dataclass(frozen=True)
class Bytes(Dtype, lang.Singleton):
    pass
