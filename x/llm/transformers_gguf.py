"""
https://huggingface.co/docs/transformers/en/gguf

https://github.com/ggerganov/llama.cpp/blob/master/convert_hf_to_gguf.py

tokenizer = tfm.AutoTokenizer.from_pretrained(model_id, gguf_file=filename)

LlamaForCausalLM(
    model_id,
    config=LlamaConfig(...),
    adapter_kwargs={},
    gguf_file='tinyllama-1.1b-chat-v1.0.Q6_K.gguf',
)
"""
import os.path

import gguf
import transformers as tfm


def _manual():
    pretrained_model_name_or_path = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
    gguf_file = 'tinyllama-1.1b-chat-v1.0.Q6_K.gguf'

    #

    resolved_config_file = tfm.utils.cached_file(
        pretrained_model_name_or_path,
        tfm.utils.CONFIG_NAME,
        _raise_exceptions_for_gated_repo=False,
        _raise_exceptions_for_missing_entries=False,
        _raise_exceptions_for_connection_errors=False,
    )

    commit_hash = tfm.utils.extract_commit_hash(resolved_config_file, None)

    #

    kwargs = {
        '_from_auto': True,
        'gguf_file': gguf_file,
    }

    config, kwargs = tfm.AutoConfig.from_pretrained(
        pretrained_model_name_or_path,
        return_unused_kwargs=True,
        trust_remote_code=None,
        code_revision=None,
        _commit_hash=commit_hash,
        **kwargs,
    )

    model_class = tfm.models.auto.auto_factory._get_model_class(  # noqa
        config,
        tfm.AutoModelForCausalLM._model_mapping,  # noqa
    )

    model = model_class.from_pretrained(
        pretrained_model_name_or_path,
        config=config,
        **kwargs
    )

    return model


def _main() -> None:
    # model_id = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
    # filename = "tinyllama-1.1b-chat-v1.0.Q6_K.gguf"
    # model = tfm.AutoModelForCausalLM.from_pretrained(model_id, gguf_file=filename)

    #

    model = _manual()
    print(model)

    #

    model_id = 'meta-llama/Llama-3.2-3B-Instruct'
    model_path = os.path.expanduser('~/.cache/nexa/hub/official/Llama3.2-3B-Instruct/q4_0.gguf')
    from transformers.modeling_gguf_pytorch_utils import load_gguf_checkpoint
    gguf_checkpoint = load_gguf_checkpoint(model_path, return_tensors=True)
    config = tfm.AutoConfig.for_model(**gguf_checkpoint['config'])
    model = tfm.AutoModelForCausalLM.from_pretrained(model_id, config=config)
    print(model)


if __name__ == '__main__':
    _main()
