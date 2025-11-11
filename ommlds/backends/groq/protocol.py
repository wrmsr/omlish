"""
https://console.groq.com/docs/api-reference#chat-create
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
        role: ta.Literal['user'] = 'user'

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class AssistantMessage(Message, lang.Final):
        content: str | ta.Sequence[str] | None = None
        name: str | None = None
        reasoning: str | None = None
        role: ta.Literal['assistant'] = 'assistant'

        @dc.dataclass(frozen=True, kw_only=True)
        @_set_class_marshal_options
        class ToolCall(lang.Final):
            @dc.dataclass(frozen=True, kw_only=True)
            @_set_class_marshal_options
            class Function(lang.Final):
                arguments: str
                name: str

            function: Function
            id: str
            type: ta.Literal['function'] = 'function'

        tool_calls: ta.Sequence[ToolCall] | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class ToolMessage(Message, lang.Final):
        content: str | ta.Sequence[str]
        role: ta.Literal['tool'] = 'tool'
        tool_call_id: str

    messages: ta.Sequence[Message]
    model: str
    citation_options: ta.Literal['enabled', 'disabled'] | None = None
    compound_custom: ta.Mapping[str, ta.Any] | None = None
    disable_tool_validation: bool | None = None
    documents: ta.Sequence[ta.Mapping[str, ta.Any]] | None = None
    frequency_penalty: float | None = None
    include_reasoning: bool | None = None
    logit_bias: ta.Mapping[str, ta.Any] | None = None
    logprobs: bool | None = None
    max_completion_tokens: int | None = None
    n: int | None = None
    parallel_tool_calls: bool | None = None
    presence_penalty: float | None = None
    reasoning_effort: ta.Literal['none', 'default', 'low', 'medium', 'high'] | None = None
    reasoning_format: ta.Literal['hidden', 'raw', 'parsed'] | None = None
    response_format: ta.Any | None = None
    search_settings: ta.Mapping[str, ta.Any] | None = None
    seed: int | None = None
    service_tier: ta.Literal['auto', 'on_demand', 'flex', 'performance', 'null'] | None = None
    stop: str | ta.Sequence[str] | None = None
    store: bool | None = None
    stream: bool | None = None
    stream_options: ta.Mapping[str, ta.Any] | None = None
    temperature: float | None = None
    ool_choice: str | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class Tool(lang.Final):
        @dc.dataclass(frozen=True, kw_only=True)
        @_set_class_marshal_options
        class Function(lang.Final):
            description: str | None = None
            name: str
            parameters: ta.Mapping[str, ta.Any] | None = None  # json schema
            strict: bool | None = None

        function: Function
        type: ta.Literal['function', 'browser_search', 'code_interpreter'] = 'function'

    tools: ta.Sequence[Tool] | None = None

    top_logprobs: int | None = None
    top_p: float | None = None
    user: str | None = None


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
    usage_breakdown: ta.Mapping[str, ta.Any] | None = None
    x_groq: ta.Mapping[str, ta.Any] | None = None
    service_tier: str | None = None


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

    x_groq: ta.Mapping[str, ta.Any] | None = None
    service_tier: str | None = None
    usage: ta.Mapping[str, ta.Any] | None = None


##


msh.register_global_module_import('._marshal', __package__)
