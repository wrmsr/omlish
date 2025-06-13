"""
https://huggingface.co/docs/transformers/en/gguf

https://github.com/ggerganov/llama.cpp/blob/master/convert_hf_to_gguf.py


LlamaForCausalLM(
    model_id,
    config=LlamaConfig(...),
    adapter_kwargs={},
    gguf_file='tinyllama-1.1b-chat-v1.0.Q6_K.gguf',
)
"""
import collections
import os.path
import sys

import gguf  # noqa

import transformers as tfm
import transformers.modeling_gguf_pytorch_utils
import transformers.models.llama.configuration_llama
import transformers.models.llama.modeling_llama


def _manual(
        model_id: str,
        gguf_file: str,
):
    resolved_config_file = tfm.utils.cached_file(
        model_id,
        tfm.utils.CONFIG_NAME,
        _raise_exceptions_for_gated_repo=False,
        _raise_exceptions_for_missing_entries=False,
        _raise_exceptions_for_connection_errors=False,
    )

    commit_hash = tfm.utils.extract_commit_hash(
        resolved_config_file,
        None,
    )

    config_dict, unused_kwargs = tfm.PretrainedConfig.get_config_dict(
        model_id,
        _from_auto=True,
        gguf_file=gguf_file,
        return_unused_kwargs=True,
        _commit_hash=commit_hash,
    )

    unused_kwargs.pop('return_unused_kwargs')
    unused_kwargs.pop('gguf_file')
    if unused_kwargs:
        raise Exception(unused_kwargs)

    config_class = tfm.models.llama.configuration_llama.LlamaConfig
    config = config_class(**config_dict)

    gguf_path = tfm.utils.cached_file(
        model_id,
        gguf_file,
        revision='main',
        _raise_exceptions_for_gated_repo=False,
        _raise_exceptions_for_missing_entries=False,
        _commit_hash=commit_hash,
    )

    state_dict = tfm.modeling_gguf_pytorch_utils.load_gguf_checkpoint(
        gguf_path,
        return_tensors=True,
    )['tensors']

    config.name_or_path = model_id

    config._attn_implementation = 'sdpa'
    config._attn_implementation_autoset = True

    model_class = tfm.models.llama.modeling_llama.LlamaForCausalLM
    with tfm.modeling_utils.no_init_weights(_enable=True):
        model = model_class(config)

    model.tie_weights()

    model_state_dict = model.state_dict()
    expected_keys = list(model_state_dict)
    prefix = model.base_model_prefix

    loaded_keys = list(state_dict)

    if prefix:
        has_prefix_module = any(s.startswith(prefix) for s in loaded_keys)
        expects_prefix_module = any(s.startswith(prefix) for s in expected_keys)
    else:
        has_prefix_module = False
        expects_prefix_module = False

    remove_prefix_from_model = not has_prefix_module and expects_prefix_module
    add_prefix_to_model = has_prefix_module and not expects_prefix_module

    if remove_prefix_from_model:
        _prefix = f'{prefix}.'
        expected_keys = [s[len(_prefix) :] if s.startswith(_prefix) else s for s in expected_keys]
    elif add_prefix_to_model:
        expected_keys = ['.'.join([prefix, s]) for s in expected_keys]

    model.tie_weights()

    model.apply(model._initialize_weights)

    start_prefix = ''
    model_to_load = model

    error_msgs, offload_index, state_dict_index = tfm.modeling_utils._load_state_dict_into_meta_model(  # noqa
        model_to_load,
        state_dict,
        start_prefix,
        expected_keys,
    )

    if error_msgs:
        raise Exception(error_msgs)
    if offload_index is not None:
        raise Exception(offload_index)
    if state_dict_index is not None:
        raise Exception(state_dict_index)

    model.tie_weights()

    model.eval()

    return model


def _main() -> None:
    model_id = 'TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF'
    gguf_file = 'tinyllama-1.1b-chat-v1.0.Q6_K.gguf'

    #

    # model = tfm.AutoModelForCausalLM.from_pretrained(model_id, gguf_file=filename)

    #

    model = _manual(model_id, gguf_file)

    print(model)

    tokenizer = tfm.AutoTokenizer.from_pretrained(model_id, gguf_file=gguf_file)

    pipeline = tfm.pipeline(
        'text-generation',
        model=model,
        tokenizer=tokenizer,
        **{
            **dict(
                # device='mps' if sys.platform == 'darwin' else 'cuda',
            ),
        },
    )
    print(pipeline('How are you?'))

    #

    model_id = 'QuantFactory/Meta-Llama-3-8B-GGUF'
    file_name = 'Meta-Llama-3-8B.Q8_0.gguf'

    import huggingface_hub as hf
    model_path = hf.hf_hub_download(repo_id=model_id, filename=file_name)

    from transformers.modeling_gguf_pytorch_utils import load_gguf_checkpoint
    gguf_checkpoint = load_gguf_checkpoint(model_path, return_tensors=True)
    config = tfm.AutoConfig.for_model(**gguf_checkpoint['config'])
    model = tfm.AutoModelForCausalLM.from_pretrained(model_id, config=config)
    print(model)


if __name__ == '__main__':
    _main()
