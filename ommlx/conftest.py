from omlish.testing.pytest import plugins as ptp
from omlish.testing.pytest.inject.harness import harness  # noqa


def pytest_addhooks(pluginmanager):
    ptp.add_hooks(pluginmanager)

    ptp.depskip.register(
        pluginmanager,
        [r'ommlx/llamacpp/.*\.py'],
        [r'llama_cpp(\..*)?'],
    )

    ptp.depskip.register(
        pluginmanager,
        [r'ommlx/mlx/.*\.py'],
        [r'mlx(\..*)?', r'mlx_lm(\..*)?', r'transformers(\..*)?'],
    )

    ptp.depskip.register(
        pluginmanager,
        [r'ommlx/torch/.*\.py'],
        [r'torch(\..*)?'],
    )
