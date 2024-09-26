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
