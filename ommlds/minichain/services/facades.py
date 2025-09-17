import typing as ta

from omlish import check
from omlish import dataclasses as dc

from ..types import Option
from ..types import Output
from .requests import Request
from .responses import Response
from .services import Service


RequestV = ta.TypeVar('RequestV')
OptionT = ta.TypeVar('OptionT', bound=Option)

ResponseV = ta.TypeVar('ResponseV')
OutputT = ta.TypeVar('OutputT', bound=Output)


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(
    allow_dynamic_dunder_attrs=True,
    terse_repr=True,
)
class ServiceFacade(
    ta.Generic[
        RequestV,
        OptionT,
        ResponseV,
        OutputT,
    ],
):
    service: Service[
        Request[
            RequestV,
            OptionT,
        ],
        Response[
            ResponseV,
            OutputT,
        ],
    ]

    def invoke(self, request: Request[RequestV, OptionT]) -> ta.Awaitable[Response[ResponseV, OutputT]]:
        return self.service.invoke(request)

    @ta.overload
    def __call__(self, request: Request[RequestV, OptionT]) -> ta.Awaitable[Response[ResponseV, OutputT]]:
        ...

    @ta.overload
    def __call__(self, v: RequestV, *options: OptionT) -> ta.Awaitable[Response[ResponseV, OutputT]]:
        ...

    def __call__(self, o, *args):
        if isinstance(o, Request):
            check.empty(args)
            request = o
        else:
            request = Request(o, args)
        return self.invoke(request)


def facade(
    service: Service[
        Request[
            RequestV,
            OptionT,
        ],
        Response[
            ResponseV,
            OutputT,
        ],
    ],
) -> ServiceFacade[
    RequestV,
    OptionT,
    ResponseV,
    OutputT,
]:
    return ServiceFacade(service)
