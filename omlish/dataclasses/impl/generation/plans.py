"""
TODO:
 - sha1 is slow :/ key by repr but name by sha1
"""
import dataclasses as dc
import re
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
    def render(self) -> str:
        return _render(self)


##


_WS_PAT = re.compile(r'\s+')


def _render(plans: Plans) -> str:
    return _WS_PAT.sub('', repr(plans.tup))
