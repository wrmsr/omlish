import dataclasses as dc

from ... import lang
from ... import reflect as rfl
from .configs import Config


##


@dc.dataclass(frozen=True)
class ReflectOverride(Config, lang.Final):
    rty: rfl.Type
