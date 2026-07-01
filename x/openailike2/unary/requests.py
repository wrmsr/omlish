from omlish import dataclasses as dc

from ..requests import RequestBase
from ..requests import RequestMessage


##


@dc.dataclass(frozen=True, kw_only=True)
class Request[
    RequestMessageT: RequestMessage = RequestMessage,
](
    RequestBase[
        RequestMessageT,
    ],
):
    pass
