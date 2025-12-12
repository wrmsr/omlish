"""
https://inference-docs.cerebras.ai/resources/openai
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


##


def _set_class_marshal_options(cls):
    msh.update_object_metadata(
        cls,
        field_defaults=msh.FieldMetadata(
            options=msh.FieldOptions(
                omit_if=lang.is_none,
            ),
        ),
    )

    return cls


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ChatCompletionRequest(lang.Final):
    model: str

    ##
    # messages

    @dc.dataclass(frozen=True, kw_only=True)
    class Message(lang.Sealed, lang.Abstract):
        pass

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class SystemMessage(Message, lang.Final):
        content: str | ta.Sequence[str]
        name: str | None = None
        role: ta.Literal['system'] = 'system'

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class UserMessage(Message, lang.Final):
        content: str | ta.Sequence[str]
        name: str | None = None
        role: ta.Literal['system'] = 'system'

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class AssistantMessage(Message, lang.Final):
        content: str | ta.Sequence[str] | None = None
        name: str | None = None
        reasoning: str | ta.Iterable[ta.Mapping[str, ta.Any]] | None = None

        @dc.dataclass(frozen=True, kw_only=True)
        @_set_class_marshal_options
        class ToolCall(lang.Final):
            id: str

            @dc.dataclass(frozen=True, kw_only=True)
            @_set_class_marshal_options
            class Function(lang.Final):
                arguments: str
                name: str

            function: Function

            type: ta.Literal['function'] = 'function'

        tool_calls: ta.Iterable[ToolCall] | None = None

        role: ta.Literal['assistant'] = 'assistant'

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class ToolMessage(Message, lang.Final):
        content: str
        tool_call_id: str
        name: str | None = None
        role: ta.Literal['tool'] = 'tool'

    messages: ta.Iterable[Message] | None = None

    ##
    # tools

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class Tool(lang.Final):
        @dc.dataclass(frozen=True, kw_only=True)
        @_set_class_marshal_options
        class Function(lang.Final):
            name: str
            description: str | None = None
            parameters: ta.Mapping[str, ta.Any] | None = None
            strict: bool | None = None

        function: Function
        type: ta.Literal['function'] = 'function'

    tools: ta.Iterable[Tool] | None = None

    tool_choice: ta.Literal['none', 'auto', 'required'] | None = None

    parallel_tool_calls: bool | None = None  # NOT SUPPORTED

    ##
    # response format

    @dc.dataclass(frozen=True, kw_only=True)
    class ResponseFormat(lang.Sealed, lang.Abstract):
        pass

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class TextResponseFormat(ResponseFormat, lang.Final):
        type: ta.Literal['text'] = 'text'

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class JsonObjectResponseFormat(ResponseFormat, lang.Final):
        type: ta.Literal['json_object'] = 'json_object'

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class JsonSchemaResponseFormat(ResponseFormat, lang.Final):
        @dc.dataclass(frozen=True, kw_only=True)
        @_set_class_marshal_options
        class JsonSchema(lang.Final):
            name: str
            description: str | None = None
            schema: ta.Mapping[str, ta.Any] | None = None
            strict: bool | None = None

        json_schema: JsonSchema

        type: ta.Literal['json_schema'] = 'json_schema'

    response_format: ResponseFormat | None = None

    ##
    # streaming

    stream: bool | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class StreamOptions(lang.Final):
        include_usage: bool | None = None

    stream_options: StreamOptions | None = None

    ##
    # generation misc

    disable_reasoning: bool | None = None
    reasoning_effort: ta.Literal['low', 'medium', 'high'] | None = None

    max_completion_tokens: int | None = None
    max_tokens: int | None = None
    min_completion_tokens: int | None = None
    min_tokens: int | None = None

    temperature: float | None = None
    seed: int | None = None

    n: int | None = None
    top_logprobs: int | None = None
    top_p: float | None = None

    frequency_penalty: float | None = None  # NOT SUPPORTED
    presence_penalty: float | None = None  # NOT SUPPORTED

    stop: str | ta.Sequence[str] | None = None

    logit_bias: ta.Any | None = None  # NOT SUPPORTED
    logprobs: bool | None = None

    prediction: ta.Mapping[str, ta.Any] | None = None

    ##
    # request misc

    service_tier: ta.Literal['auto', 'default', 'flex', 'priority'] | None = None  # NOT SUPPORTED


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ExecutedTool(lang.Final):
    arguments: str
    index: int
    type: str
    browser_results: ta.Sequence[ta.Any] | None = None
    code_results: ta.Sequence[ta.Any] | None = None
    output: str | None = None
    search_results: ta.Any | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ChatCompletionResponse(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class Choice(lang.Final):
        finish_reason: ta.Literal['stop', 'length', 'tool_calls', 'function_call']
        index: int
        logprobs: ta.Mapping[str, ta.Any] | None = None

        @dc.dataclass(frozen=True, kw_only=True)
        @_set_class_marshal_options
        class Message(lang.Final):
            annotations: ta.Sequence[ta.Mapping[str, ta.Any]] | None = None
            content: str | None = None

            executed_tools: ta.Sequence[ExecutedTool] | None = None

            reasoning: str | None = None
            role: ta.Literal['assistant'] = 'assistant'

            @dc.dataclass(frozen=True, kw_only=True)
            @_set_class_marshal_options
            class ToolCall(lang.Final):
                id: str

                @dc.dataclass(frozen=True, kw_only=True)
                @_set_class_marshal_options
                class Function(lang.Final):
                    arguments: str
                    name: str

                function: Function
                type: ta.Literal['function'] = 'function'

            tool_calls: ta.Sequence[ToolCall] | None = None

        message: Message

    choices: ta.Sequence[Choice]
    created: int
    id: str
    model: str
    object: ta.Literal['chat.completion'] = 'chat.completion'
    system_fingerprint: str
    usage: ta.Mapping[str, ta.Any] | None = None
    time_info: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ChatCompletionChunk(lang.Final):
    id: str
    object: ta.Literal['chat.completion.chunk'] = 'chat.completion.chunk'
    created: int
    model: str
    system_fingerprint: str

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class Choice(lang.Final):
        index: int

        @dc.dataclass(frozen=True, kw_only=True)
        @_set_class_marshal_options
        class Delta(lang.Final):
            role: str | None = None
            content: str | None = None

            channel: str | None = None
            reasoning: str | None = None

            @dc.dataclass(frozen=True, kw_only=True)
            @_set_class_marshal_options
            class ToolCall(lang.Final):
                index: int
                id: str | None = None

                @dc.dataclass(frozen=True, kw_only=True)
                @_set_class_marshal_options
                class Function(lang.Final):
                    arguments: str | None = None
                    name: str | None = None

                function: Function | None = None

                type: ta.Literal['function'] = 'function'

            tool_calls: ta.Sequence[ToolCall] | None = None

            executed_tools: ta.Sequence[ExecutedTool] | None = None

        delta: Delta
        logprobs: ta.Mapping[str, ta.Any] | None = None
        finish_reason: ta.Literal['stop', 'length', 'tool_calls', 'function_call'] | None = None

    choices: ta.Sequence[Choice]

    usage: ta.Mapping[str, ta.Any] | None = None
    time_info: ta.Mapping[str, ta.Any] | None = None


##


msh.register_global_module_import('._marshal', __package__)
