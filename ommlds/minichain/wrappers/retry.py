"""
TODO:
 - RetryServiceRequestMetadata
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
from ..services import StreamResponseSink
from ..services import WrappedOptionT
from ..services import WrappedOutputT
from ..services import WrappedRequest
from ..services import WrappedRequestV
from ..services import WrappedResponse
from ..services import WrappedResponseV
from ..services import WrappedService
from ..services import WrappedStreamOutputT
from ..services import WrappedStreamResponse
from ..services import WrappedStreamService
from ..services import WrapperService
from ..services import WrapperStreamService
from ..services import new_stream_response
from .metadata import RetryServiceResponseMetadata


AnyRetryService: ta.TypeAlias = ta.Union[
    'RetryService',
    'RetryStreamService',
]


##


@dc.dataclass()
class RetryServiceMaxRetriesExceededError(Exception):
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(__cause__={self.__cause__!r})'


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
            child: WrappedService,
            *,
            max_retries: int | None = None,
    ) -> None:
        super().__init__(child)

        if max_retries is None:
            max_retries = self.DEFAULT_MAX_RETRIES
        self._max_retries = max_retries

    async def invoke(self, request: WrappedRequest) -> WrappedResponse:
        n = 0

        while True:
            try:
                resp = await self._child.invoke(request)

            except Exception as e:  # noqa
                if n < self._max_retries:
                    n += 1
                    continue

                raise RetryServiceMaxRetriesExceededError from e

            return resp.with_metadata(RetryServiceResponseMetadata(
                num_retries=n,
                retry_service=self,
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
            child: WrappedStreamService,
            *,
            max_retries: int | None = None,
    ) -> None:
        super().__init__(child)

        if max_retries is None:
            max_retries = self.DEFAULT_MAX_RETRIES
        self._max_retries = max_retries

    async def invoke(self, request: WrappedRequest) -> WrappedStreamResponse:
        n = 0

        while True:
            try:
                async with Resources.new() as rs:
                    in_resp = await self._child.invoke(request)
                    in_vs = await rs.enter_async_context(in_resp.v)

                    async def inner(sink: StreamResponseSink[WrappedResponseV]) -> ta.Sequence[WrappedOutputT] | None:
                        async for v in in_vs:
                            await sink.emit(v)

                        return in_vs.outputs

                    # FIXME: ??
                    # if (ur := tv.as_collection(request.options).get(UseResources)) is not None:

                    return await new_stream_response(
                        rs,
                        inner,
                        in_resp.outputs,
                        metadata=[
                            *in_resp.metadata,
                            RetryServiceResponseMetadata(
                                num_retries=n,
                                retry_service=self,
                            ),
                        ],
                    )

            except Exception as e:  # noqa
                if n < self._max_retries:
                    n += 1
                    continue

                raise RetryServiceMaxRetriesExceededError from e
