import typing as ta

from omlish import check
from omlish import lang

from ..services.requests import Request
from ..services.responses import Response
from ..services.services import Service
from ..types import Option
from ..types import Output


WrappedRequestV = ta.TypeVar('WrappedRequestV')
WrappedOptionT = ta.TypeVar('WrappedOptionT', bound=Option)

WrappedResponseV = ta.TypeVar('WrappedResponseV')
WrappedOutputT = ta.TypeVar('WrappedOutputT', bound=Output)


WrappedRequest: ta.TypeAlias = Request[
    WrappedRequestV,
    WrappedOptionT,
]

WrappedResponse: ta.TypeAlias = Response[
    WrappedResponseV,
    WrappedOutputT,
]

WrappedService: ta.TypeAlias = Service[
    WrappedRequest,
    WrappedResponse,
]


##


class WrapperService(
    lang.Abstract,
    ta.Generic[
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
        super().__init__()

        self._service = service


class MultiWrapperService(
    lang.Abstract,
    ta.Generic[
        WrappedRequestV,
        WrappedOptionT,
        WrappedResponseV,
        WrappedOutputT,
    ],
):
    def __init__(
            self,
            *services: WrappedService,
    ) -> None:
        super().__init__()

        self._services = check.not_empty(services)
