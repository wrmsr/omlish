import typing as ta

from omlish.testing.pytest import plugins as ptp


BACKEND_DEPSKIP_MODULES: ta.Mapping[str, ta.Sequence[str]] = {
    'llamacpp': ['llama_cpp'],
    'mlx': [
        'mlx',
        'mlx_lm',
        'transformers',
    ],
    'sentencepiece': ['sentencepiece'],
    'tiktoken': ['tiktoken'],
    'tinygrad': ['tinygrad'],
    'tokenizers': ['tokenizers'],
    'torch': ['torch'],
    'transformers': [
        'sentencetransformers',
        'transformers',
    ],
}


def pytest_addhooks(pluginmanager):
    for mod, imp_mods in BACKEND_DEPSKIP_MODULES.items():
        ptp.depskip.module_register(
            pluginmanager,
            [f'{__package__}.{mod}'],
            imp_mods,
        )
