import typing as ta
import uuid

from omlish import check

from ..metadata import RequestUuid
from ..metadata import ResponseUuid
from ..services import WrappedOptionT
from ..services import WrappedOutputT
from ..services import WrappedRequest
from ..services import WrappedRequestV
from ..services import WrappedResponse
from ..services import WrappedResponseV
from ..services import WrappedService
from ..services import WrapperService


##


class RequestResponseUuidAddingService(
    WrapperService[
        WrappedRequestV,
        WrappedOptionT,
        WrappedResponseV,
        WrappedOutputT,
    ],
):
    def __init__(
            self,
            child: WrappedService,
            *,
            uuid_factory: ta.Callable[[], uuid.UUID] | None = None,
    ) -> None:
        super().__init__(child)

        if uuid_factory is None:
            uuid_factory = uuid.uuid4
        self._uuid_factory = uuid_factory

    async def invoke(self, request: WrappedRequest) -> WrappedResponse:
        try:
            req_um = request.metadata[RequestUuid]
        except KeyError:
            req_um = RequestUuid(self._uuid_factory())
            request = request.with_metadata(req_um)

        response = await self._child.invoke(request)

        try:
            req_um2 = response.metadata[RequestUuid]
        except KeyError:
            response = response.with_metadata(req_um)
        else:
            check.equal(req_um, req_um2)

        try:
            res_um = response.metadata[ResponseUuid]  # noqa
        except KeyError:
            response = response.with_metadata(ResponseUuid(self._uuid_factory()))

        return response
