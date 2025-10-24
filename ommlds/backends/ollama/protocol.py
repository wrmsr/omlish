"""
https://docs.ollama.com/api
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=dc.opt_repr)
class Options:
    # loading
    numa: bool | None = None
    num_ctx: int | None = None
    num_batch: int | None = None
    num_gpu: int | None = None
    main_gpu: int | None = None
    low_vram: bool | None = None
    f16_kv: bool | None = None
    logits_all: bool | None = None
    vocab_only: bool | None = None
    use_mmap: bool | None = None
    use_mlock: bool | None = None
    embedding_only: bool | None = None
    num_thread: int | None = None

    # querying
    num_keep: int | None = None
    seed: int | None = None
    num_predict: int | None = None
    top_k: int | None = None
    top_p: float | None = None
    tfs_z: float | None = None
    typical_p: float | None = None
    repeat_last_n: int | None = None
    temperature: float | None = None
    repeat_penalty: float | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None
    mirostat: int | None = None
    mirostat_tau: float | None = None
    mirostat_eta: float | None = None
    penalize_newline: bool | None = None
    stop: ta.Sequence[str] | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
class BaseRequest(lang.Abstract):
    model: str


@dc.dataclass(frozen=True, kw_only=True)
class BaseStreamableRequest(BaseRequest, lang.Abstract):
    stream: bool | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
class BaseGenerateRequest(BaseStreamableRequest, lang.Abstract):
    options: Options | None = None
    format: ta.Literal['', 'json'] | None = None  # TODO: jsonschema
    keep_alive: float | str | None = None


@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=dc.opt_repr)
class GenerateRequest(BaseGenerateRequest):
    prompt: str | None = None
    suffix: str | None = None
    system: str | None = None
    template: str | None = None
    context: ta.Sequence[int] | None = None
    raw: bool | None = None
    images: ta.Sequence[bytes] | None = None
    think: bool | ta.Literal['low', 'medium', 'high'] | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
class BaseGenerateResponse(lang.Abstract):
    model: str | None = None
    created_at: str | None = None
    done: bool | None = None
    done_reason: str | None = None
    total_duration: int | None = None
    load_duration: int | None = None
    prompt_eval_count: int | None = None
    prompt_eval_duration: int | None = None
    eval_count: int | None = None
    eval_duration: int | None = None


@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=dc.opt_repr)
class GenerateResponse(BaseGenerateResponse):
    response: str
    thinking: str | None = None
    context: ta.Sequence[int] | None = None


##


Role: ta.TypeAlias = ta.Literal[
    'system',
    'user',
    'assistant',
    'tool',
]


@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=dc.opt_repr)
class Message:
    role: Role
    content: str | None = None
    thinking: str | None = None
    images: ta.Sequence[bytes] | None = None
    tool_name: str | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    class ToolCall:
        @dc.dataclass(frozen=True, kw_only=True)
        class Function:
            name: str
            arguments: ta.Mapping[str, ta.Any]

        function: Function

    tool_calls: ta.Sequence[ToolCall] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=dc.opt_repr)
class Tool:
    type: str | None = 'function'

    @dc.dataclass(frozen=True, kw_only=True)
    @dc.extra_class_params(default_repr_fn=dc.opt_repr)
    class Function:
        name: str | None = None
        description: str | None = None
        parameters: ta.Any | None = None

    function: Function | None = None


@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=dc.opt_repr)
class ChatRequest(BaseGenerateRequest):
    messages: ta.Sequence[Message] | None = None
    tools: ta.Sequence[Tool] | None = None
    think: bool | ta.Literal['low', 'medium', 'high'] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=dc.opt_repr)
class ChatResponse(BaseGenerateResponse):
    message: Message
