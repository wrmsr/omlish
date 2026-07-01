import dataclasses as dc
import typing as ta


##


@dc.dataclass(frozen=True, kw_only=True)
class StreamOptions:
    include_usage: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class StreamRequest[
    MessageT: RequestMessage = RequestMessage,
    StreamOptionsT: StreamOptions = StreamOptions,
](
    RequestBase[
        MessageT,
    ],
):
    stream: ta.Literal[True] = True
    stream_options: StreamOptionsT | None = None
