"""
https://github.com/openshift/docker-distribution/tree/master/docs/spec

runners/metal
  --model ~/.ollama/models/blobs/sha256-74701a8c35f6c8d9a4b91f3f3497643001d63e0c7a84e085bed452548fa88d45
  --ctx-size 8192
  --batch-size 512
  --embedding
  --log-disable
  --n-gpu-layers 17
  --parallel 4
  --port 49319

curl -XPOST -H 'Content-Type: application/json' http://127.0.0.1:49319/completion -d '
{
  "cache_prompt" : true,
  "frequency_penalty" : 0,
  "image_data" : [ ],
  "main_gpu" : 0,
  "min_p" : 0,
  "mirostat" : 0,
  "mirostat_eta" : 0.1,
  "mirostat_tau" : 5,
  "n_keep" : 4,
  "n_predict" : 81920,
  "penalize_nl" : true,
  "presence_penalty" : 0,
  "prompt" : "<|start_header_id|>system<|end_header_id|>\n\nCutting Knowledge Date: December 2023\n\n<|eot_id|><|start_header_id|>user<|end_header_id|>\n\nWhy is the sky blue?<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
  "repeat_last_n" : 64,
  "repeat_penalty" : 1.1,
  "seed" : -1,
  "stop" : null,
  "stream" : true,
  "temperature" : 0.8,
  "tfs_z" : 1,
  "top_k" : 40,
  "top_p" : 0.9,
  "typical_p" : 1
}
'

unknown backend opts:
 - n_ctx
 - model
 - dynatemp_range
 - dynatemp_exponent
 - penalty_prompt_tokens
 - use_penalty_prompt_tokens
 - max_tokens
 - n_discard
 - ignore_eos
 - stream
 - logit_bias
 - n_probs
 - min_keep
 - grammar
 - samplers
"""
import enum
import json
import operator
import os.path
import typing as ta

from omlish import dataclasses as dc
from omlish import marshal as msh
from omlish import lang


class Capability(enum.Enum):
    COMPLETION = 'completion'
    TOOLS = 'tools'
    INSERT = 'insert'


class Role(enum.Enum):
    USER = 'user'
    ASSISTANT = 'assistant'
    SYSTEM = 'system'


@dc.dataclass(frozen=True)
class RootFs(lang.Final):
    type: str
    diff_ids: ta.Sequence[str]


@dc.dataclass(frozen=True)
class ConfigV2(lang.Final):
    model_format: str
    model_family: str
    model_families: ta.Sequence[str]
    model_type: str
    file_type: str

    architecture: str  # required by spec
    os: str  # required by spec
    rootfs: RootFs  # required by spec


ToolCallFunctionArguments: ta.TypeAlias = ta.Mapping[str, ta.Any]


@dc.dataclass(frozen=True)
class ToolCallFunction(lang.Final):
    name: str
    arguments: ToolCallFunctionArguments


@dc.dataclass(frozen=True)
class ToolCall(lang.Final):
    function: ToolCallFunction


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['images', 'tool_calls'], omit_if=operator.not_)
class Message(lang.Final):
    role: str
    content: str
    images: ta.Sequence[bytes]
    tool_calls: ta.Sequence[ToolCall]


@dc.dataclass(frozen=True)
class Model(lang.Final):
    name: str
    config: ConfigV2
    short_name: str
    model_path: str
    parent_model: str
    adapter_paths: ta.Sequence[str]
    projector_paths: ta.Sequence[str]
    system: str
    license: ta.Sequence[str]
    digest: str
    options: ta.Mapping[str, ta.Any]

    messages: ta.Sequence[Message]

    template: str


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=operator.not_)
class Runner:
    num_ctx: int = 0
    num_batch: int = 0
    num_gpu: int = 0
    main_gpu: int = 0
    low_vram: bool = False
    f16_kv: bool = False
    logits_all: bool = False
    vocab_only: bool = False
    use_mmap: bool | None = None
    use_mlock: bool = False
    num_thread: int = 0


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=operator.not_)
class Options(Runner):
    num_keep: int = 0  # be: n_keep
    seed: int = 0  # be:
    num_predict: int = 0  # be: n_predict
    top_k: int = 0  # be:
    top_p: float = 0.  # be:
    min_p: float = 0.  # be:
    tfs_z: float = 0.  # be:
    typical_p: float = 0.  # be:
    repeat_last_n: int = 0  # be:
    temperature: float = 0.0  # be:
    repeat_penalty: float = 0.  # be:
    presence_penalty: float = 0.  # be:
    frequency_penalty: float = 0.  # be:
    mirostat: int = 0  # be:
    mirostat_tau: float = 0.  # be:
    mirostat_eta: float = 0.  # be:
    penalize_newline: bool = False  # be: penalize_nl
    stop: ta.Sequence[str] = ()  # be:


DEFAULT_OPTIONS = Options(
    num_ctx=2048,
    num_batch=512,
    num_gpu=-1,
    num_thread=0,
    low_vram=False,
    f16_kv=True,
    use_mlock=False,
    use_mmap=None,

    num_predict=-1,

    num_keep=4,
    temperature=0.8,
    top_k=40,
    top_p=0.9,
    tfs_z=1.0,
    typical_p=1.0,
    repeat_last_n=64,
    repeat_penalty=1.1,
    presence_penalty=0.0,
    frequency_penalty=0.0,
    mirostat=0,
    mirostat_tau=5.0,
    mirostat_eta=0.1,
    penalize_newline=True,
    seed=-1,
)


@dc.dataclass(frozen=True)
class ModelDetails:
    parent_model: str
    format: str
    family: str
    families: ta.Sequence[str]
    parameter_size: str
    quantization_level: str


def _main() -> None:
    model_name = 'llama3.2'
    model_version = '3b'

    ollama_dir = os.path.expanduser('~/.ollama')
    registry_name = 'registry.ollama.ai'
    model_manifest_dir = os.path.join(
        ollama_dir,
        'models',
        'manifests',
        registry_name,
        'library',
        model_name,
    )

    model_manifest_file = os.path.join(model_manifest_dir, model_version)
    with open(model_manifest_file) as f:
        model_manifest = json.load(f)

    print(model_manifest)


if __name__ == '__main__':
    _main()
