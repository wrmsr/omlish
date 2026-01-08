"""
TODO:
 - tenacity shit
  - exception filter - retryable vs not
   - explicit RetryableError wrapper?
  - sleep
   - jitter
 - log, on retry / on except callbacks, blah blah
 - stream retry:
  - failed to open
  - failed during stream
   - buffer and replay??
  - accept death mid-stream?
  - ** probably **: cannot sanely impose any nontrivial stream retry strat at this layer -
"""
import typing as ta

from omlish import dataclasses as dc

from ..resources import Resources
from ..stream.services import StreamResponseSink
from ..stream.services import new_stream_response
from ..types import Output
from .services import WrappedOptionT
from .services import WrappedOutputT
from .services import WrappedRequest
from .services import WrappedRequestV
from .services import WrappedResponse
from .services import WrappedResponseV
from .services import WrappedService
from .services import WrapperService
from .stream import WrappedStreamOutputT
from .stream import WrappedStreamResponse
from .stream import WrappedStreamService
from .stream import WrapperStreamService


AnyRetryService: ta.TypeAlias = ta.Union[
    'RetryService',
    'RetryStreamService',
]


##


@dc.dataclass()
class RetryServiceMaxRetriesExceededError(Exception):
    pass


@dc.dataclass(frozen=True)
class RetryServiceOutput(Output):
    retry_service: AnyRetryService
    num_retries: int


##


class RetryService(
    WrapperService[
        WrappedRequestV,
        WrappedOptionT,
        WrappedResponseV,
        WrappedOutputT,
    ],
):
    DEFAULT_MAX_RETRIES: ta.ClassVar[int] = 3

    def __init__(
            self,
            service: WrappedService,
            *,
            max_retries: int | None = None,
    ) -> None:
        super().__init__(service)

        if max_retries is None:
            max_retries = self.DEFAULT_MAX_RETRIES
        self._max_retries = max_retries

    async def invoke(self, request: WrappedRequest) -> WrappedResponse:
        n = 0

        while True:
            try:
                resp = await self._service.invoke(request)

            except Exception as e:  # noqa
                if n < self._max_retries:
                    n += 1
                    continue

                raise RetryServiceMaxRetriesExceededError from e

            return resp.with_outputs(RetryServiceOutput(
                retry_service=self,
                num_retries=n,
            ))

        raise RuntimeError  # unreachable


##


class RetryStreamService(
    WrapperStreamService[
        WrappedRequestV,
        WrappedOptionT,
        WrappedResponseV,
        WrappedOutputT,
        WrappedStreamOutputT,
    ],
):
    DEFAULT_MAX_RETRIES: ta.ClassVar[int] = 3

    def __init__(
            self,
            service: WrappedStreamService,
            *,
            max_retries: int | None = None,
    ) -> None:
        super().__init__(service)

        if max_retries is None:
            max_retries = self.DEFAULT_MAX_RETRIES
        self._max_retries = max_retries

    async def invoke(self, request: WrappedRequest) -> WrappedStreamResponse:
        n = 0

        while True:
            try:
                async with Resources.new() as rs:
                    in_resp = await self._service.invoke(request)
                    in_vs = await rs.enter_async_context(in_resp.v)

                    async def inner(sink: StreamResponseSink[WrappedResponseV]) -> ta.Sequence[WrappedOutputT] | None:
                        async for v in in_vs:
                            await sink.emit(v)

                        return in_vs.outputs

                    outs = [
                        *in_resp.outputs,
                        RetryServiceOutput(
                            retry_service=self,
                            num_retries=n,
                        ),
                    ]

                    # FIXME: ??
                    # if (ur := tv.as_collection(request.options).get(UseResources)) is not None:

                    return await new_stream_response(
                        rs,
                        inner,
                        outs,
                    )

            except Exception as e:  # noqa
                if n < self._max_retries:
                    n += 1
                    continue

                raise RetryServiceMaxRetriesExceededError from e
