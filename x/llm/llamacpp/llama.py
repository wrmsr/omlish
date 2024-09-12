import dataclasses as dc
import typing as ta

import llama_cpp


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
