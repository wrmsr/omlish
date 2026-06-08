"""https://platform.openai.com/docs/api-reference/responses/create"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .._common import _set_class_marshal_options


##
# Input content parts


class ResponsesInputContentPart(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class InputTextResponsesInputContentPart(ResponsesInputContentPart, lang.Final):
    text: str


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class OutputTextResponsesInputContentPart(ResponsesInputContentPart, lang.Final):
    text: str

    annotations: ta.Sequence[ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class InputImageResponsesInputContentPart(ResponsesInputContentPart, lang.Final):
    image_url: str | None = None
    file_id: str | None = None
    detail: ta.Literal['low', 'high', 'auto'] | None = None


##
# Input items


class ResponsesInputItem(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class MessageResponsesInputItem(ResponsesInputItem, lang.Final):
    role: ta.Literal[
        'system',
        'developer',
        'user',
        'assistant',
    ]

    content: str | ta.Sequence[ResponsesInputContentPart]

    id: str | None = None
    status: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class FunctionCallResponsesInputItem(ResponsesInputItem, lang.Final):
    call_id: str
    name: str
    arguments: str

    id: str | None = None
    status: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class FunctionCallOutputResponsesInputItem(ResponsesInputItem, lang.Final):
    call_id: str
    output: str

    id: str | None = None
    status: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ReasoningResponsesInputItem(ResponsesInputItem, lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class SummaryText(lang.Final):
        text: str

        type: ta.Literal['summary_text'] = dc.xfield('summary_text', repr=False)

    summary: ta.Sequence[SummaryText] = ()

    id: str | None = None
    content: ta.Sequence[ta.Any] | None = None
    encrypted_content: str | None = None
    status: str | None = None


##
# Tools


class ResponsesTool(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class FunctionResponsesTool(ResponsesTool, lang.Final):
    """Note: unlike chat-completions tools, responses function tools are flat (name at the top level)."""

    name: str

    description: str | None = None
    parameters: ta.Mapping[str, ta.Any] | None = None
    strict: bool | None = None


##
# Request


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ResponsesRequest(lang.Final):
    model: str

    input: str | ta.Sequence[ResponsesInputItem]

    instructions: str | None = None

    tools: ta.Sequence[ResponsesTool] | None = None
    tool_choice: ta.Any | None = None
    parallel_tool_calls: bool | None = None

    max_output_tokens: int | None = None
    temperature: float | None = None
    top_p: float | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class Reasoning(lang.Final):
        effort: ta.Literal['minimal', 'low', 'medium', 'high'] | None = None
        summary: ta.Literal['auto', 'concise', 'detailed'] | None = None

    reasoning: Reasoning | None = None

    previous_response_id: str | None = None
    store: bool | None = None
    stream: bool | None = None

    include: ta.Sequence[str] | None = None
    metadata: ta.Mapping[str, str] | None = None
    truncation: ta.Literal['auto', 'disabled'] | None = None
    user: str | None = None
