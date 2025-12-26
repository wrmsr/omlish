import re
import typing as ta

from omlish import lang

from .ops import LeafOp
from .ops import Op


##


class InternalOp(Op, lang.Abstract):
    pass


##


@ta.final
class Regex(InternalOp, LeafOp, lang.Final):
    def __init__(self, pat: re.Pattern) -> None:
        super().__init__()

        self._pat = pat

    @property
    def pat(self) -> re.Pattern:
        return self._pat

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._pat!r})'
