"""
TODO:
 - stream lol
  - take first open vs take first chunk
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..services.services import Service
from ..types import Output
from .services import MultiWrapperService
from .services import WrappedOptionT
from .services import WrappedOutputT
from .services import WrappedRequest
from .services import WrappedRequestV
from .services import WrappedResponse
from .services import WrappedResponseV
from .stream import WrappedStreamOutputT
from .stream import WrapperStreamService


with lang.auto_proxy_import(globals()):
    import asyncio


AnyFirstInWinsService: ta.TypeAlias = ta.Union[
    'FirstInWinsService',
    'FirstInWinsStreamService',
]


##


@dc.dataclass()
class FirstInWinsServiceCancelledError(Exception):
    e: BaseException


class FirstInWinsServiceExceptionGroup(ExceptionGroup):
    pass


@dc.dataclass(frozen=True)
class FirstInWinsServiceOutput(Output):
    first_in_wins_service: AnyFirstInWinsService
    response_service: Service
    service_exceptions: ta.Mapping[Service, Exception] | None = None


##


class FirstInWinsService(
    MultiWrapperService[
        WrappedRequestV,
        WrappedOptionT,
        WrappedResponseV,
        WrappedOutputT,
    ],
    lang.Abstract,
):
    pass


##


class FirstInWinsStreamService(
    WrapperStreamService[
        WrappedRequestV,
        WrappedOptionT,
        WrappedResponseV,
        WrappedOutputT,
        WrappedStreamOutputT,
    ],
    lang.Abstract,
):
    pass


##


class AsyncioFirstInWinsService(
    FirstInWinsService[
        WrappedRequestV,
        WrappedOptionT,
        WrappedResponseV,
        WrappedOutputT,
    ],
):
    async def invoke(self, request: WrappedRequest) -> WrappedResponse:
        tasks: list = []
        services_by_task: dict = {}
        for svc in self._services:
            task: asyncio.Task = asyncio.create_task(svc.invoke(request))  # type: ignore[arg-type]
            tasks.append(task)
            services_by_task[task] = svc

        failures_by_service: dict[Service, Exception] = {}

        try:
            pending = set(tasks)

            while pending:
                done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

                for t in done:
                    svc = services_by_task[t]

                    try:
                        response = t.result()
                    except asyncio.CancelledError as exc:
                        failures_by_service[svc] = FirstInWinsServiceCancelledError(exc)
                        continue
                    except Exception as exc:  # noqa
                        failures_by_service[svc] = exc
                        continue

                    for p in pending:
                        p.cancel()

                    await asyncio.gather(*pending, return_exceptions=True)

                    return response.with_outputs(FirstInWinsServiceOutput(
                        self,
                        svc,
                        failures_by_service,
                    ))

            raise FirstInWinsServiceExceptionGroup(
                'All service calls failed',
                list(failures_by_service.values()),
            )

        finally:
            for t in tasks:
                if not t.done():
                    t.cancel()

            await asyncio.gather(*tasks, return_exceptions=True)
