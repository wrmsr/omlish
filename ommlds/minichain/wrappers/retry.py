"""
TODO:
 - tenacity shit
  - exception filter
  - sleep
   - jitter
"""
import typing as ta

from omlish import dataclasses as dc

from ..types import Output
from .services import WrappedOptionT
from .services import WrappedOutputT
from .services import WrappedRequest
from .services import WrappedRequestV
from .services import WrappedResponse
from .services import WrappedResponseV
from .services import WrappedService
from .services import WrapperService


##


@dc.dataclass(frozen=True)
class RetryServiceMaxRetriesExceededError(Exception):
    pass


@dc.dataclass(frozen=True)
class RetryServiceOutput(Output):
    retry_service: 'RetryService'
    num_retries: int


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
