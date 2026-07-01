import dataclasses as dc
import typing as ta




##


@dc.dataclass(frozen=True, kw_only=True)
class Request[
    MessageT: RequestMessage = RequestMessage,
    ToolT: Tool = Tool,
    ToolChoiceT: ToolChoiceOption = ToolChoiceOption,
    ResponseFormatT: ResponseFormat = ResponseFormat,
](
    RequestBase[
        MessageT,
        ToolT,
        ToolChoiceT,
        ResponseFormatT,
    ],
):
    stream: ta.Literal[False] | None = None
