import dataclasses as dc

from ... import lang
from ... import reflect as rfl
from ... import typedvalues as tv
from .configs import Config


##


@dc.dataclass(frozen=True)
class ReflectOverride(Config, tv.UniqueTypedValue, lang.Final):
    rty: rfl.Type
