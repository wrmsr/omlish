"""
TODO:
 - sha1 is slow :/ key by repr but name by sha1
"""
import dataclasses as dc
import hashlib
import typing as ta

from omlish import lang

from .base import Plan


##


@dc.dataclass(frozen=True)
class Plans:
    tup: tuple[Plan, ...]

    def __iter__(self) -> ta.Iterator[Plan]:
        return iter(self.tup)

    @lang.cached_function
    def render(self) -> str:
        return _render(self)

    @lang.cached_function
    def digest(self) -> str:
        return _digest(self.render())


##


def _render(plans: Plans) -> str:
    return repr(plans.tup)


def _digest(rendered_plans: str) -> str:
    m = hashlib.sha1()  # noqa
    m.update(rendered_plans.encode('utf-8'))
    return m.hexdigest()
