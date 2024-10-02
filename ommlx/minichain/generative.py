from omlish import dataclasses as dc
from omlish import lang

from .options import Option
from .options import UniqueOption


##


class Generative(lang.Abstract):
    pass


##


class GenerativeRequestOption(Option, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class TopK(GenerativeRequestOption, UniqueOption, lang.Final):
    k: int


@dc.dataclass(frozen=True)
class Temperature(GenerativeRequestOption, UniqueOption, lang.Final):
    f: float


@dc.dataclass(frozen=True)
class MaxTokens(GenerativeRequestOption, UniqueOption, lang.Final):
    n: int
