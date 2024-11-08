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

    #

    kwargs = dict(
        _from_auto=True,
        gguf_file=gguf_file,
        return_unused_kwargs=True,
        trust_remote_code=None,
        code_revision=None,
        _commit_hash=commit_hash,
    )

    # config, kwargs = tfm.AutoConfig.from_pretrained(
    #     model_id,
    #     **kwargs,
    # )

    kwargs.pop("trust_remote_code", None)
    kwargs.pop("code_revision", None)

    config_dict, unused_kwargs = tfm.PretrainedConfig.get_config_dict(
        model_id,
        **kwargs,
    )

    #

    # config_class = tfm.models.auto.configuration_auto.CONFIG_MAPPING[config_dict["model_type"]]
    # config, kwargs = config_class.from_dict(config_dict, **unused_kwargs)

    unused_kwargs.pop("return_unused_kwargs", False)
    unused_kwargs.pop("_from_auto", None)
    unused_kwargs.pop("_from_pipeline", None)
    # The commit hash might have been updated in the `config_dict`, we don't want the kwargs to erase that update.
    if "_commit_hash" in unused_kwargs and "_commit_hash" in config_dict:
        unused_kwargs["_commit_hash"] = config_dict["_commit_hash"]
    config_class = tfm.models.llama.configuration_llama.LlamaConfig
    config = config_class(**config_dict)
    kwargs = unused_kwargs

    #

    # model_class = tfm.models.auto.auto_factory._get_model_class(  # noqa
    #     config,
    #     tfm.AutoModelForCausalLM._model_mapping,  # noqa
    # )
    # model = model_class.from_pretrained(
    #     model_id,
    #     config=config,
    #     **kwargs
    # )

    model_class = tfm.models.llama.modeling_llama.LlamaForCausalLM

    from transformers.modeling_gguf_pytorch_utils import load_gguf_checkpoint

    cached_file_kwargs = {
        "cache_dir": None,
        "force_download": False,
        "proxies": None,
        "resume_download": None,
        "local_files_only": False,
        "token": None,
        "user_agent": {'file_type': 'model', 'framework': 'pytorch', 'from_auto_class': False},
        "revision": 'main',
        "subfolder": '',
        "_raise_exceptions_for_gated_repo": False,
        "_raise_exceptions_for_missing_entries": False,
        "_commit_hash": commit_hash,
    }

    gguf_path = tfm.utils.cached_file(model_id, gguf_file, **cached_file_kwargs)

    state_dict = load_gguf_checkpoint(gguf_path, return_tensors=True)["tensors"]

    loaded_state_dict_keys = list(state_dict.keys())

    config.name_or_path = model_id

    init_contexts = [tfm.modeling_utils.no_init_weights(_enable=True)]

    config._attn_implementation = "sdpa"
    config._attn_implementation_autoset = True

    with tfm.utils.ContextManagers(init_contexts):
        # Let's make sure we don't run the init function of buffer modules
        model = model_class(config)

    #

    return model


def _main() -> None:
    model_id = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
    gguf_file = "tinyllama-1.1b-chat-v1.0.Q6_K.gguf"

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
