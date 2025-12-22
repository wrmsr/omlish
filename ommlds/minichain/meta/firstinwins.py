import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from ..services.requests import Request
from ..services.responses import Response
from ..services.services import Service
from ..types import Option
from ..types import Output


with lang.auto_proxy_import(globals()):
    import asyncio


RequestV = ta.TypeVar('RequestV')
OptionT = ta.TypeVar('OptionT', bound=Option)

ResponseV = ta.TypeVar('ResponseV')
OutputT = ta.TypeVar('OutputT', bound=Output)


##


@dc.dataclass(frozen=True)
class FirstInWinsServiceCancelledError(Exception):
    e: BaseException


class FirstInWinsServiceExceptionGroup(ExceptionGroup):
    pass


@dc.dataclass(frozen=True)
class FirstInWinsServiceOutput(Output):
    first_in_wins_service: 'FirstInWinsService'
    response_service: Service
    service_exceptions: ta.Mapping[Service, Exception] | None = None


class FirstInWinsService(
    lang.Abstract,
    ta.Generic[
        RequestV,
        OptionT,
        ResponseV,
        OutputT,
    ],
):
    def __init__(
            self,
            *services: Service[
                Request[
                    RequestV,
                    OptionT,
                ],
                Response[
                    ResponseV,
                    OutputT,
                ],
            ],
    ) -> None:
        super().__init__()

        self._services = check.not_empty(services)


##


class AsyncioFirstInWinsService(
    FirstInWinsService[
        RequestV,
        OptionT,
        ResponseV,
        OutputT,
    ],
):
    async def invoke(self, request: Request[RequestV, OptionT]) -> Response[ResponseV, OutputT]:
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
