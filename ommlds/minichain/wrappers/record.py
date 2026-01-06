"""
TODO:
 - final sream outputs
"""
import datetime
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..services.requests import Request
from ..services.responses import Response
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


##


@dc.dataclass(frozen=True, kw_only=True)
class RecordServiceEvent:
    dt: datetime.datetime = dc.field(default_factory=lang.utcnow)

    req: Request | None = None

    resp: Response | None = None
    exc: BaseException | None = None

    stream_v: lang.Maybe[ta.Any] = lang.empty()


##


class RecordService(
    WrapperService[
        WrappedRequestV,
        WrappedOptionT,
        WrappedResponseV,
        WrappedOutputT,
    ],
):
    def __init__(
            self,
            service: WrappedService,
    ) -> None:
        super().__init__(service)

        self._events: list[RecordServiceEvent] = []

    async def invoke(self, request: WrappedRequest) -> WrappedResponse:
        self._events.append(RecordServiceEvent(req=request))

        try:
            resp = await self._service.invoke(request)

        except Exception as e:  # noqa
            self._events.append(RecordServiceEvent(req=request, exc=e))

            raise

        self._events.append(RecordServiceEvent(req=request, resp=resp))

        return resp


##


class RecordStreamService(
    WrapperStreamService[
        WrappedRequestV,
        WrappedOptionT,
        WrappedResponseV,
        WrappedOutputT,
        WrappedStreamOutputT,
    ],
):
    def __init__(
            self,
            service: WrappedStreamService,
    ) -> None:
        super().__init__(service)

        self._events: list[RecordServiceEvent] = []

    async def invoke(self, request: WrappedRequest) -> WrappedStreamResponse:
        self._events.append(RecordServiceEvent(req=request))

        try:
            resp = await self._service.invoke(request)

        except Exception as e:  # noqa
            self._events.append(RecordServiceEvent(req=request, exc=e))

            raise

        self._events.append(RecordServiceEvent(req=request, resp=resp))

        async def inner(sink):  # noqa
            async with resp.v as st:
                async for v in st:
                    self._events.append(RecordServiceEvent(req=request, resp=resp, stream_v=v))

                    await sink(v)

        # return dc.replace(resp, v=inner())

        raise NotImplementedError
