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
    async def inner():
        lst: list = []
        async with (await WrappedFooStreamService(FooStreamService()).invoke(Request('hi there!'))).v as it:
            async for e in it:
                lst.append(e)
        return lst

    lst = lang.sync_await(inner())
    assert lst == [c + '!?' for c in 'hi there!']
