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
import os.path
import json


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
