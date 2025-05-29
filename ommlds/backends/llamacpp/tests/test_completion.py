import os.path

from omlish.testing import pytest as ptu


@ptu.skip.if_cant_import('llama_cpp')
def test_llamacpp_completion():
    model_path = os.path.join(
        os.path.expanduser('~/.cache/huggingface/hub'),
        'models--QuantFactory--Meta-Llama-3-8B-GGUF',
        'snapshots',
        '1ca85c857dce892b673b988ad0aa83f2cb1bbd19',
        'Meta-Llama-3-8B.Q8_0.gguf',
    )

    # model_path = os.path.join(
    #     os.path.expanduser('~/Library/Caches/llama.cpp'),
    #     'bartowski_Qwen2.5-7B-Instruct-GGUF_Qwen2.5-7B-Instruct-Q4_K_M.gguf',
    # )

    from ..logging import install_logging_hook
    install_logging_hook()

    import llama_cpp
    llm = llama_cpp.Llama(
        model_path=model_path,
    )

    output = llm.create_completion(
        'Is water dry?',
        max_tokens=64,
        # stop=['\n'],
    )

    msg = output['choices'][0]['text']  # type: ignore
    assert msg
