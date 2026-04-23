import typing as ta

from omlish import lang

from ..services import Service
from ..services import StreamOptions
from ..services import StreamResponse
from ..services.requests import Request
from ..types import Output
from .services import WrappedOptionT
from .services import WrappedOutputT
from .services import WrappedRequestV
from .services import WrappedResponseV


WrappedStreamOutputT = ta.TypeVar('WrappedStreamOutputT', bound=Output)


WrappedStreamOptions: ta.TypeAlias = WrappedOptionT | StreamOptions

WrappedStreamRequest: ta.TypeAlias = Request[
    WrappedRequestV,
    WrappedStreamOptions,
]

WrappedStreamResponse: ta.TypeAlias = StreamResponse[
    WrappedResponseV,
    WrappedOutputT,
    WrappedStreamOutputT,
]

WrappedStreamService: ta.TypeAlias = Service[
    WrappedStreamRequest,
    WrappedStreamResponse,
]


##


class WrapperStreamService(
    lang.Abstract,
    ta.Generic[
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
        super().__init__()

        self._service = service
