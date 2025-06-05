import typing as ta

from omlish import check
from omlish import dataclasses as dc

from .requests import Request
from .requests import RequestOption
from .responses import Response
from .responses import ResponseOutput
from .services import Service


RequestV = ta.TypeVar('RequestV')
RequestOptionT = ta.TypeVar('RequestOptionT', bound=RequestOption)

ResponseV = ta.TypeVar('ResponseV')
ResponseOutputT = ta.TypeVar('ResponseOutputT', bound=ResponseOutput)


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(
    allow_dynamic_dunder_attrs=True,
    terse_repr=True,
)
class ServiceFacade(
    Service[
        Request[
            RequestV,
            RequestOptionT,
        ],
        Response[
            ResponseV,
            ResponseOutputT,
        ],
    ],
    ta.Generic[
        RequestV,
        RequestOptionT,
        ResponseV,
        ResponseOutputT,
    ],
):
    service: Service[
        Request[
            RequestV,
            RequestOptionT,
        ],
        Response[
            ResponseV,
            ResponseOutputT,
        ],
    ]

    def invoke(self, request: Request[RequestV, RequestOptionT]) -> Response[ResponseV, ResponseOutputT]:
        return self.service.invoke(request)

    @ta.overload
    def __call__(self, request: Request[RequestV, RequestOptionT]) -> Response[ResponseV, ResponseOutputT]:
        ...

    @ta.overload
    def __call__(self, v: RequestV, *options: RequestOptionT) -> Response[ResponseV, ResponseOutputT]:
        ...

    def __call__(self, o, *args):
        if isinstance(o, Request):
            check.empty(args)
            request = o
        else:
            request = Request(o, args)
        return self.invoke(request)
