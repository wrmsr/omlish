from omlish.testing.pytest import plugins as ptp


def pytest_addhooks(pluginmanager):
    ptp.depskip.module_register(
        pluginmanager,
        [__package__ + '.llamacpp'],
        ['llama_cpp'],
    )

    ptp.depskip.module_register(
        pluginmanager,
        [__package__ + '.mlx'],
        [
            'mlx',
            'mlx_lm',
            'transformers',
        ],
    )

    ptp.depskip.module_register(
        pluginmanager,
        [__package__ + '.sentencepiece'],
        ['sentencepiece'],
    )

    ptp.depskip.module_register(
        pluginmanager,
        [__package__ + '.tiktoken'],
        ['tiktoken'],
    )

    ptp.depskip.module_register(
        pluginmanager,
        [__package__ + '.tinygrad'],
        ['tinygrad'],
    )

    ptp.depskip.module_register(
        pluginmanager,
        [__package__ + '.tokenizers'],
        ['tokenizers'],
    )

    ptp.depskip.module_register(
        pluginmanager,
        [__package__ + '.torch'],
        ['torch'],
    )

    ptp.depskip.module_register(
        pluginmanager,
        [__package__ + '.transformers'],
        [
            'sentencetransformers',
            'transformers',
        ],
    )
