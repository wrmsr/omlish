import typing as ta

from .services import WrappedOptionT
from .services import WrappedOutputT
from .services import WrappedRequest
from .services import WrappedRequestV
from .services import WrappedResponse
from .services import WrappedResponseV
from .services import WrappedService
from .services import WrapperService


##


class UpdateOptionsService(
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
            *options: WrappedOptionT,
            discard: ta.Literal['all'] | ta.Iterable[type] | None = None,
            mode: ta.Literal['append', 'prepend', 'override', 'default'] = 'append',
    ) -> None:
        super().__init__(service)

        self._options = options
        self._discard = discard
        self._mode = mode

    async def invoke(self, request: WrappedRequest) -> WrappedResponse:
        out_request = request.with_options(
            *self._options,
            discard=self._discard,
            mode=self._mode,
        )

        return await self._service.invoke(out_request)
