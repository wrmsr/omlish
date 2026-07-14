"""https://platform.openai.com/docs/api-reference/responses/object"""
import typing as ta

from omcore import dataclasses as dc
from omcore import lang
from omcore import marshal as msh

from .._common import _set_class_marshal_options


##
# Output content parts


class ResponsesOutputContentPart(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class OutputTextResponsesOutputContentPart(ResponsesOutputContentPart, lang.Final):
    text: str

    annotations: ta.Sequence[ta.Any] | None = None
    logprobs: ta.Sequence[ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class RefusalResponsesOutputContentPart(ResponsesOutputContentPart, lang.Final):
    refusal: str


##
# Output items


class ResponsesOutputItem(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class MessageResponsesOutputItem(ResponsesOutputItem, lang.Final):
    content: ta.Sequence[ResponsesOutputContentPart]

    role: ta.Literal['assistant'] = dc.xfield('assistant', repr=False)

    id: str | None = None
    status: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class FunctionCallResponsesOutputItem(ResponsesOutputItem, lang.Final):
    call_id: str
    name: str
    arguments: str

    id: str | None = None
    status: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ReasoningResponsesOutputItem(ResponsesOutputItem, lang.Final):
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
# The response object


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ResponsesUsage(lang.Final):
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None

    input_tokens_details: ta.Mapping[str, ta.Any] | None = None
    output_tokens_details: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_options(unknown_field='x')
@_set_class_marshal_options
class ResponseToolUsage(lang.Final):
    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ResponsesResponse(lang.Final):
    id: str

    object: ta.Literal['response'] = dc.xfield('response', repr=False)

    created_at: float | None = None

    status: ta.Literal[
        'completed',
        'failed',
        'in_progress',
        'cancelled',
        'queued',
        'incomplete',
    ] | None = None

    model: str | None = None

    output: ta.Sequence[ResponsesOutputItem] = ()

    usage: ResponsesUsage | None = None

    error: ta.Any | None = None
    incomplete_details: ta.Any | None = None

    instructions: ta.Any | None = None
    tools: ta.Sequence[ta.Any] | None = None
    tool_choice: ta.Any | None = None
    parallel_tool_calls: bool | None = None

    max_output_tokens: int | None = None
    max_tool_calls: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    top_logprobs: int | None = None

    reasoning: ta.Any | None = None
    text: ta.Any | None = None

    previous_response_id: str | None = None
    store: bool | None = None
    background: bool | None = None
    truncation: str | None = None
    metadata: ta.Mapping[str, str] | None = None
    user: str | None = None
    safety_identifier: str | None = None
    prompt_cache_key: str | None = None
    service_tier: str | None = None
    billing: ta.Any | None = None
    output_text: str | None = None

    tool_usage: ResponseToolUsage | None = None

    # FIXME: lol
    presence_penalty: ta.Any | None = None
    frequency_penalty: ta.Any | None = None
    prompt_cache_retention: ta.Any | None = None
    moderation: ta.Any | None = None
    completed_at: ta.Any | None = None
