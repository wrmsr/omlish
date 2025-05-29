from omlish.testing.pytest import plugins as ptp

from ...backends.conftest import BACKEND_DEPSKIP_MODULES


def pytest_addhooks(pluginmanager):
    for mod in [
        'llamacpp',
        'mlx',
        'tinygrad',
        'transformers',
    ]:
        ptp.depskip.module_register(
            pluginmanager,
            [f'{__package__}.{mod}'],
            BACKEND_DEPSKIP_MODULES[mod],
        )
