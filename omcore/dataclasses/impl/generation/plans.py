import dataclasses as dc
import typing as ta

from .... import lang
from .base import Plan


##


@dc.dataclass(frozen=True)
class Plans:
    tup: tuple[Plan, ...]

    def __iter__(self) -> ta.Iterator[Plan]:
        return iter(self.tup)

    @lang.cached_function(no_wrapper_update=True)
    def repr(self) -> str:
        return repr(self)
