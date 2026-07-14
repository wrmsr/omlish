# ruff: noqa: I001

# https://github.com/tinygrad/tinygrad/blob/2d6d8b735506464367b0315f9a2f424e0d19f66e/examples/llama3.py
# https://github.com/tinygrad/tinygrad/blob/ef17af85c6d3f84d1e1cc084d6dee8ced3d1a33e/extra/models/llama.py


from omlish import lang as _lang


with _lang.auto_proxy_init(globals()):
    from .fetch import (  # noqa
        fetch_model,
    )

    from .llm import (  # noqa
        Llama3Llm,
        run_llm,
        run_llm_to_stop,
        RunLlmToStopResult,
    )

    from .tokenization import (  # noqa
        Tokenizer,
    )

    from .transformer import (  # noqa
        Transformer,
    )
