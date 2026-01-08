"""
TODO:
 - final stream outputs
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
@dc.extra_class_params(default_repr_fn=lang.opt_or_just_repr)
class InstrumentedServiceEvent:
    dt: datetime.datetime = dc.field(default_factory=lang.utcnow)

    req: Request | None = None

    resp: Response | None = None
    exc: BaseException | None = None

    stream_v: lang.Maybe[ta.Any] = lang.empty()


class InstrumentedServiceEventSink(ta.Protocol):
    def __call__(self, ev: InstrumentedServiceEvent) -> ta.Awaitable[None]: ...


class ListInstrumentedServiceEventSink:
    def __init__(self, lst: list[InstrumentedServiceEvent] | None = None) -> None:
        super().__init__()

        if lst is None:
            lst = []
        self._lst = lst

    @property
    def events(self) -> ta.Sequence[InstrumentedServiceEvent]:
        return self._lst

    async def __call__(self, ev: InstrumentedServiceEvent) -> None:
        self._lst.append(ev)


##


class InstrumentedService(
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
            sink: InstrumentedServiceEventSink | None = None,
    ) -> None:
        super().__init__(service)

        if sink is None:
            sink = ListInstrumentedServiceEventSink()
        self._sink = sink

    async def invoke(self, request: WrappedRequest) -> WrappedResponse:
        await self._sink(InstrumentedServiceEvent(req=request))

        try:
            resp = await self._service.invoke(request)

        except Exception as e:  # noqa
            await self._sink(InstrumentedServiceEvent(req=request, exc=e))

            raise

        await self._sink(InstrumentedServiceEvent(req=request, resp=resp))

        return resp


##


class InstrumentedStreamService(
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
            sink: InstrumentedServiceEventSink | None = None,
    ) -> None:
        super().__init__(service)

        if sink is None:
            sink = ListInstrumentedServiceEventSink()
        self._sink = sink

    async def invoke(self, request: WrappedRequest) -> WrappedStreamResponse:
        await self._sink(InstrumentedServiceEvent(req=request))

        try:
            resp = await self._service.invoke(request)

        except Exception as e:  # noqa
            await self._sink(InstrumentedServiceEvent(req=request, exc=e))

            raise

        await self._sink(InstrumentedServiceEvent(req=request, resp=resp))

        async def inner(sink):  # noqa
            async with resp.v as st:
                async for v in st:
                    await self._sink(InstrumentedServiceEvent(req=request, resp=resp, stream_v=v))

                    await sink(v)

        # return resp.with_v(inner())

        raise NotImplementedError
