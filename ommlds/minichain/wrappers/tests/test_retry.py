import pytest

from ...resources import UseResources
from ...services.requests import Request
from ...services.responses import Response
from ...stream.services import StreamResponseSink
from ...stream.services import new_stream_response
from ...types import Option
from ...types import Output
from ..retry import RetryService
from ..retry import RetryServiceMaxRetriesExceededError
from ..retry import RetryServiceOutput


##


class SuccessService:
    async def invoke(self, request: Request[int, Option]) -> Response[str, Output]:
        return Response(f'success({request.v})')


class FailNTimesServiceError(Exception):
    pass


class FailNTimesService:
    def __init__(self, fail_count: int):
        self._fail_count = fail_count
        self._attempt = 0

    async def invoke(self, request: Request[int, Option]) -> Response[str, Output]:
        if self._attempt < self._fail_count:
            self._attempt += 1
            raise FailNTimesServiceError(f'fail_attempt_{self._attempt}({request.v})')
        return Response(f'success_after_{self._fail_count}_retries({request.v})')


class AlwaysFailService:
    async def invoke(self, request: Request[int, Option]) -> Response[str, Output]:
        raise FailNTimesServiceError('always_fail')


@pytest.mark.asyncs('asyncio')
async def test_retry_success_first_try():
    r = await RetryService(SuccessService()).invoke(Request(42))
    assert r.v == 'success(42)'

    # Check that num_retries is 0 for successful first attempt
    retry_output = next(o for o in r.outputs if isinstance(o, RetryServiceOutput))
    assert retry_output.num_retries == 0


@pytest.mark.asyncs('asyncio')
async def test_retry_success_after_failures():
    # Should succeed after 2 retries (fails twice, succeeds on third attempt)
    r = await RetryService(FailNTimesService(2)).invoke(Request(42))
    assert r.v == 'success_after_2_retries(42)'

    retry_output = next(o for o in r.outputs if isinstance(o, RetryServiceOutput))
    assert retry_output.num_retries == 2


@pytest.mark.asyncs('asyncio')
async def test_retry_max_retries_exceeded():
    # Default max_retries is 3, so should fail after 3 retries (4 total attempts)
    with pytest.raises(RetryServiceMaxRetriesExceededError):
        await RetryService(AlwaysFailService()).invoke(Request(42))


@pytest.mark.asyncs('asyncio')
async def test_retry_custom_max_retries():
    # Custom max_retries of 5
    r = await RetryService(FailNTimesService(5), max_retries=5).invoke(Request(42))
    assert r.v == 'success_after_5_retries(42)'

    retry_output = next(o for o in r.outputs if isinstance(o, RetryServiceOutput))
    assert retry_output.num_retries == 5

    # Should fail with max_retries=1 when service fails twice
    with pytest.raises(RetryServiceMaxRetriesExceededError):
        await RetryService(FailNTimesService(2), max_retries=1).invoke(Request(42))


##


class SuccessStreamService:
    async def invoke(self, request: Request[str, Option]) -> Response:
        async with UseResources.or_new(request.options) as rs:
            async def inner(sink: StreamResponseSink[str]) -> list[Output] | None:
                for c in request.v:
                    await sink.emit(c + '!')
                return []
            return await new_stream_response(rs, inner)


class FailNTimesStreamServiceError(Exception):
    pass


class FailNTimesStreamService:
    def __init__(self, fail_count: int):
        self._fail_count = fail_count
        self._attempt = 0

    async def invoke(self, request: Request[str, Option]) -> Response:
        if self._attempt < self._fail_count:
            self._attempt += 1
            raise FailNTimesStreamServiceError(f'fail_attempt_{self._attempt}({request.v})')

        from ...resources import UseResources
        from ...stream.services import StreamResponseSink
        from ...stream.services import new_stream_response

        async with UseResources.or_new(request.options) as rs:
            async def inner(sink: StreamResponseSink[str]) -> list[Output] | None:
                for c in f'success_after_{self._fail_count}_retries({request.v})':
                    await sink.emit(c)
                return []
            return await new_stream_response(rs, inner)


class AlwaysFailStreamService:
    async def invoke(self, request: Request[str, Option]) -> Response:
        raise FailNTimesStreamServiceError('always_fail')


@pytest.mark.asyncs('asyncio')
async def test_retry_stream_success_first_try():
    from ..retry import RetryStreamService

    r = await RetryStreamService(SuccessStreamService()).invoke(Request('hi'))
    lst: list = []
    async with r.v as it:
        async for e in it:
            lst.append(e)
    assert lst == ['h!', 'i!']

    # Check that num_retries is 0 for successful first attempt
    retry_output = next(o for o in r.outputs if isinstance(o, RetryServiceOutput))
    assert retry_output.num_retries == 0


@pytest.mark.asyncs('asyncio')
async def test_retry_stream_success_after_failures():
    from ..retry import RetryStreamService

    # Should succeed after 2 retries (fails twice, succeeds on third attempt)
    r = await RetryStreamService(FailNTimesStreamService(2)).invoke(Request('hi'))
    lst: list = []
    async with r.v as it:
        async for e in it:
            lst.append(e)
    assert lst == list('success_after_2_retries(hi)')

    retry_output = next(o for o in r.outputs if isinstance(o, RetryServiceOutput))
    assert retry_output.num_retries == 2


@pytest.mark.asyncs('asyncio')
async def test_retry_stream_max_retries_exceeded():
    from ..retry import RetryStreamService

    # Default max_retries is 3, so should fail after 3 retries (4 total attempts)
    with pytest.raises(RetryServiceMaxRetriesExceededError):
        await RetryStreamService(AlwaysFailStreamService()).invoke(Request('hi'))


@pytest.mark.asyncs('asyncio')
async def test_retry_stream_custom_max_retries():
    from ..retry import RetryStreamService

    # Custom max_retries of 5
    r = await RetryStreamService(FailNTimesStreamService(5), max_retries=5).invoke(Request('hi'))
    lst: list = []
    async with r.v as it:
        async for e in it:
            lst.append(e)
    assert lst == list('success_after_5_retries(hi)')

    retry_output = next(o for o in r.outputs if isinstance(o, RetryServiceOutput))
    assert retry_output.num_retries == 5

    # Should fail with max_retries=1 when service fails twice
    with pytest.raises(RetryServiceMaxRetriesExceededError):
        await RetryStreamService(FailNTimesStreamService(2), max_retries=1).invoke(Request('hi'))
