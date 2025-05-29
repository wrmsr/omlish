from omlish.testing.pytest import plugins as ptp


def pytest_addhooks(pluginmanager):
    ptp.depskip.register(
        pluginmanager,
        [r'ommlds/backends/llamacpp/.*\.py'],
        [
            r'llama_cpp(\..*)?',
        ],
    )

    ptp.depskip.register(
        pluginmanager,
        [r'ommlds/backends/mlx/.*\.py'],
        [
            r'mlx(\..*)?',
            r'mlx_lm(\..*)?',
            r'transformers(\..*)?',
        ],
    )

    ptp.depskip.register(
        pluginmanager,
        [r'ommlds/backends/sentencepiece/.*\.py'],
        [
            r'sentencepiece(\..*)?',
        ],
    )

    ptp.depskip.register(
        pluginmanager,
        [r'ommlds/backends/tiktoken/.*\.py'],
        [
            r'tiktoken(\..*)?',
        ],
    )

    ptp.depskip.register(
        pluginmanager,
        [r'ommlds/backends/tinygrad/.*\.py'],
        [
            r'tinygrad(\..*)?',
        ],
    )

    ptp.depskip.register(
        pluginmanager,
        [r'ommlds/backends/tokenizers/.*\.py'],
        [
            r'tokenizers(\..*)?',
        ],
    )

    ptp.depskip.register(
        pluginmanager,
        [r'ommlds/backends/torch/.*\.py'],
        [
            r'torch(\..*)?',
        ],
    )

    ptp.depskip.register(
        pluginmanager,
        [r'ommlds/backends/transformers/.*\.py'],
        [
            r'transformers(\..*)?',
            r'sentencetransformers(\..*)?',
        ],
    )
