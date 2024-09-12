import dataclasses as dc
import typing as ta

import llama_cpp


##


@dc.dataclass(frozen=True)
class LlamaOpts:
    model_path: str

    # Model Params
    n_gpu_layers: int = 0
    split_mode: int = llama_cpp.LLAMA_SPLIT_MODE_LAYER
    main_gpu: int = 0
    tensor_split: ta.Sequence[float] | None = None
    rpc_servers: str | None = None
    vocab_only: bool = False
    use_mmap: bool = True
    use_mlock: bool = False
    kv_overrides: ta.Mapping[str, int | float | str] | None = None

    # Context Param
    seed: int = llama_cpp.LLAMA_DEFAULT_SEED
    n_ctx: int = 512
    n_batch: int = 512
    n_threads: int | None = None
    n_threads_batch: int | None = None
    rope_scaling_type: int | None = llama_cpp.LLAMA_ROPE_SCALING_TYPE_UNSPECIFIED
    pooling_type: int = llama_cpp.LLAMA_POOLING_TYPE_UNSPECIFIED
    rope_freq_base: float = 0.0
    rope_freq_scale: float = 0.0
    yarn_ext_factor: float = -1.0
    yarn_attn_factor: float = 1.0
    yarn_beta_fast: float = 32.0
    yarn_beta_slow: float = 1.0
    yarn_orig_ctx: int = 0
    logits_all: bool = False
    embedding: bool = False
    offload_kqv: bool = True
    flash_attn: bool = False

    # Sampling Params
    last_n_tokens_size: int = 64

    # LoRA Params
    lora_base: str | None = None
    lora_scale: float = 1.0
    lora_path: str | None = None

    # Backend Params
    numa: bool | int = False

    # Chat Format Params
    chat_format: str | None = None
    chat_handler: llama_chat_format.LlamaChatCompletionHandler | None = None

    # Speculative Decoding
    draft_model: LlamaDraftModel | None = None

    # Tokenizer Override
    tokenizer: BaseLlamaTokenizer | None = None

    # KV cache quantization
    type_k: int | None = None
    type_v: int | None = None

    # Misc
    spm_infill: bool = False
    verbose: bool = True


##


@dc.dataclass(frozen=True)
class CompletionRequest:
    prompt: str | ta.Sequence[int]
    suffix: str | None = None
    max_tokens: int | None = 16
    temperature: float = 0.8
    top_p: float = 0.95
    min_p: float = 0.05
    typical_p: float = 1.0
    logprobs: int | None = None
    echo: bool = False
    stop: str | ta.Sequence[str] | None = ()
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    repeat_penalty: float = 1.0
    top_k: int = 40
    stream: bool = False
    seed: int | None = None
    tfs_z: float = 1.0
    mirostat_mode: int = 0
    mirostat_tau: float = 5.0
    mirostat_eta: float = 0.1
    model: str | None = None
    stopping_criteria: StoppingCriteriaList | None = None
    logits_processor: LogitsProcessorList | None = None
    grammar: LlamaGrammar | None = None
    logit_bias: ta.Mapping[str, float] | None = None


#


class CompletionLogprobs(ta.TypedDict):
    text_offset: ta.Sequence[int]
    token_logprobs: ta.Sequence[float | None]
    tokens: ta.Sequence[str]
    top_logprobs: ta.Sequence[ta.Mapping[str, float] | None]


class CompletionChoice(ta.TypedDict):
    text: str
    index: int
    logprobs: CompletionLogprobs | None
    finish_reason: ta.Literal['stop', 'length'] | None


class CompletionUsage(ta.TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class CompletionResponse(ta.TypedDict):
    id: str
    object: ta.Literal['text_completion']
    created: int
    model: str
    choices: ta.Sequence[CompletionChoice]
    usage: ta.NotRequired[CompletionUsage]


##


@dc.dataclass(frozen=True)
class ChatCompletionRequest:
    messages: ta.Sequence[ChatCompletionRequestMessage]
    functions: ta.Sequence[ChatCompletionFunction] | None = None
    function_call: ChatCompletionRequestFunctionCall | None = None
    tools: ta.Sequence[ChatCompletionTool] | None = None
    tool_choice: ChatCompletionToolChoiceOption | None = None
    temperature: float = 0.2
    top_p: float = 0.95
    top_k: int = 40
    min_p: float = 0.05
    typical_p: float = 1.0
    stream: bool = False
    stop: str | ta.Sequence[str] | None = ()
    seed: int | None = None
    response_format: ChatCompletionRequestResponseFormat | None = None
    max_tokens: int | None = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    repeat_penalty: float = 1.0
    tfs_z: float = 1.0
    mirostat_mode: int = 0
    mirostat_tau: float = 5.0
    mirostat_eta: float = 0.1
    model: str | None = None
    logits_processor: LogitsProcessorList | None = None
    grammar: LlamaGrammar | None = None
    logit_bias: ta.Mapping[str, float] | None = None
    logprobs: bool | None = None
    top_logprobs: int | None = None
