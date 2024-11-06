"""
https://huggingface.co/docs/transformers/en/gguf

https://github.com/ggerganov/llama.cpp/blob/master/convert_hf_to_gguf.py

tokenizer = AutoTokenizer.from_pretrained(model_id, gguf_file=filename)

LlamaForCausalLM(
    model_id,
    config=LlamaConfig(...),
    adapter_kwargs={},
    gguf_file='tinyllama-1.1b-chat-v1.0.Q6_K.gguf',
)
"""
import os.path

import gguf
import transformers
from transformers import AutoModelForCausalLM
from transformers import AutoTokenizer


def _main() -> None:
    model_id = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
    filename = "tinyllama-1.1b-chat-v1.0.Q6_K.gguf"
    model = AutoModelForCausalLM.from_pretrained(model_id, gguf_file=filename)

    model_id = 'meta-llama/Llama-3.2-3B-Instruct'
    model_path = os.path.expanduser('~/.cache/nexa/hub/official/Llama3.2-3B-Instruct/q4_0.gguf')
    from transformers.modeling_gguf_pytorch_utils import load_gguf_checkpoint
    gguf_checkpoint = load_gguf_checkpoint(model_path, return_tensors=True)
    config = transformers.AutoConfig.for_model(**gguf_checkpoint['config'])
    model = AutoModelForCausalLM.from_pretrained(model_id, config=config)

    print(model)


if __name__ == '__main__':
    _main()
