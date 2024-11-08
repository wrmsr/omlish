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

import gguf

import transformers as tfm
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

    commit_hash = tfm.utils.extract_commit_hash(resolved_config_file, None)

    kwargs = dict(
        _from_auto=True,
        gguf_file=gguf_file,
        return_unused_kwargs=True,
        _commit_hash=commit_hash,
    )

    config_dict, unused_kwargs = tfm.PretrainedConfig.get_config_dict(
        model_id,
        **kwargs,
    )

    unused_kwargs.pop('return_unused_kwargs', False)
    unused_kwargs.pop('_from_auto', None)
    unused_kwargs.pop('_from_pipeline', None)
    if '_commit_hash' in unused_kwargs and '_commit_hash' in config_dict:
        unused_kwargs['_commit_hash'] = config_dict['_commit_hash']
    config_class = tfm.models.llama.configuration_llama.LlamaConfig
    config = config_class(**config_dict)
    kwargs = unused_kwargs

    model_class = tfm.models.llama.modeling_llama.LlamaForCausalLM

    kwargs.pop('gguf_file', None)

    from transformers.modeling_gguf_pytorch_utils import load_gguf_checkpoint

    gguf_path = tfm.utils.cached_file(
        model_id,
        gguf_file,
        revision='main',
        _raise_exceptions_for_gated_repo=False,
        _raise_exceptions_for_missing_entries=False,
        _commit_hash=commit_hash,
    )

    state_dict = load_gguf_checkpoint(gguf_path, return_tensors=True)['tensors']

    loaded_state_dict_keys = list(state_dict.keys())

    config.name_or_path = model_id

    init_contexts = [tfm.modeling_utils.no_init_weights(_enable=True)]

    config._attn_implementation = 'sdpa'
    config._attn_implementation_autoset = True

    with tfm.utils.ContextManagers(init_contexts):
        model = model_class(config)

    #

    model.tie_weights()

    model_state_dict = model.state_dict()
    expected_keys = list(model_state_dict.keys())
    prefix = model.base_model_prefix

    loaded_keys = loaded_state_dict_keys

    if len(prefix) > 0:
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

    #

    model.tie_weights()

    model.eval()

    #

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

    model_id = 'meta-llama/Llama-3.2-3B-Instruct'
    model_path = os.path.expanduser('~/.cache/nexa/hub/official/Llama3.2-3B-Instruct/q4_0.gguf')
    from transformers.modeling_gguf_pytorch_utils import load_gguf_checkpoint
    gguf_checkpoint = load_gguf_checkpoint(model_path, return_tensors=True)
    config = tfm.AutoConfig.for_model(**gguf_checkpoint['config'])
    model = tfm.AutoModelForCausalLM.from_pretrained(model_id, config=config)
    print(model)


if __name__ == '__main__':
    _main()
