import typing as ta

from omlish import lang

from ...services import Request
from ..wrap import WrappedStreamService
from .test_services import FooStreamService


class WrappedFooStreamService(WrappedStreamService):
    @ta.override
    def _process_value(self, v: str) -> ta.Iterable[str]:
        return [v + '?']


def test_wrap():
    with lang.sync_await(WrappedFooStreamService(FooStreamService()).invoke(Request('hi there!'))).v as it:
        lst = list(it)
    assert lst == [c + '!?' for c in 'hi there!']
