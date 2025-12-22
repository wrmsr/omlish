import asyncio

import pytest

from ...services.requests import Request
from ...services.responses import Response
from ...types import Option
from ...types import Output
from ..firstinwins import AsyncioFirstInWinsService
from ..firstinwins import FirstInWinsServiceExceptionGroup


class FastSuccessService:
    async def invoke(self, request: Request[int, Option]) -> Response[str, Output]:
        await asyncio.sleep(.2)
        return Response(f'fast_success({request.v})')


class SlowSuccessService:
    async def invoke(self, request: Request[int, Option]) -> Response[str, Output]:
        await asyncio.sleep(1)
        return Response(f'slow_success({request.v})')


class FastFailServiceError(Exception):
    pass


class FastFailService:
    async def invoke(self, request: Request[int, Option]) -> Response[str, Output]:
        await asyncio.sleep(.1)
        raise FastFailServiceError(f'fast_fail({request.v})')


@pytest.mark.asyncs('asyncio')
async def test_asyncio_first_in_wins():
    r = await AsyncioFirstInWinsService(
        FastSuccessService(),
        SlowSuccessService(),
        FastFailService(),
    ).invoke(Request(42))
    assert r.v == 'fast_success(42)'

    with pytest.raises(FirstInWinsServiceExceptionGroup) as eg:
        await AsyncioFirstInWinsService(
            FastFailService(),
            FastFailService(),
            FastFailService(),
        ).invoke(Request(42))
    assert len(eg.value.exceptions) == 3
    assert all(isinstance(e, FastFailServiceError) for e in eg.value.exceptions)
