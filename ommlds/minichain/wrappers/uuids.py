import uuid

from omlish import check

from ..metadata import RequestUuid
from ..metadata import ResponseUuid
from .services import WrappedOptionT
from .services import WrappedOutputT
from .services import WrappedRequest
from .services import WrappedRequestV
from .services import WrappedResponse
from .services import WrappedResponseV
from .services import WrapperService


##


class RequestResponseUuidAddingService(
    WrapperService[
        WrappedRequestV,
        WrappedOptionT,
        WrappedResponseV,
        WrappedOutputT,
    ],
):
    async def invoke(self, request: WrappedRequest) -> WrappedResponse:
        try:
            req_um = request.metadata[RequestUuid]
        except KeyError:
            req_um = RequestUuid(uuid.uuid4())
            request = request.with_metadata(req_um)

        response = await self._service.invoke(request)

        try:
            req_um2 = response.metadata[RequestUuid]
        except KeyError:
            response = response.with_metadata(req_um)
        else:
            check.equal(req_um, req_um2)

        try:
            res_um = response.metadata[ResponseUuid]  # noqa
        except KeyError:
            response = response.with_metadata(ResponseUuid(uuid.uuid4()))

        return response
