import typing as ta

from ...services import Request
from ..wrap import WrappedStreamService
from .test_services import FooStreamService


class WrappedFooStreamService(WrappedStreamService):
    def _process_vs(self, vs: ta.Iterator[str]) -> ta.Iterator[str]:
        for v in vs:
            yield v + '?'


def test_wrap():
    with WrappedFooStreamService(FooStreamService()).invoke(Request('hi there!')).v as it:
        lst = list(it)
    assert lst == [c + '!?' for c in 'hi there!']
