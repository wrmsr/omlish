import typing as ta

from omlish import dataclasses as dc

from ..requests import RequestBase
from ..requests import RequestMessage


##


@dc.dataclass(frozen=True, kw_only=True)
class StreamOptions:
    include_usage: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class StreamRequest[
    RequestMessageT: RequestMessage = RequestMessage,
    StreamOptionsT: StreamOptions = StreamOptions,
](
    RequestBase[
        RequestMessageT,
    ],
):
    stream: ta.Literal[True] = True
    stream_options: StreamOptionsT | None = None
