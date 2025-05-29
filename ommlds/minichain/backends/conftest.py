import typing as ta

from omlish.testing.pytest import plugins as ptp

from ...backends.conftest import BACKEND_DEPSKIP_MODULES as BASE_BACKEND_DEPSKIP_MODULES


BACKEND_DEPSKIP_MODULES: ta.Mapping[str, ta.Sequence[str]] = {
    'llamacpp': BASE_BACKEND_DEPSKIP_MODULES['llamacpp'],
    'mlx': BASE_BACKEND_DEPSKIP_MODULES['mlx'],
    'sentencepiece': ['sentencepiece'],
    'tinygrad': BASE_BACKEND_DEPSKIP_MODULES['tinygrad'],
    'tokenizers': ['tokenizers'],
    'transformers': BASE_BACKEND_DEPSKIP_MODULES['transformers'],
}


def pytest_addhooks(pluginmanager):
    for mod, imp_mods in BACKEND_DEPSKIP_MODULES.items():
        ptp.depskip.module_register(
            pluginmanager,
            [f'{__package__}.{mod}'],
            imp_mods,
        )
