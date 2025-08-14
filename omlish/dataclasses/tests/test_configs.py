from ..impl.configs import PACKAGE_CONFIG_CACHE


def test_configs():
    for _ in range(2):
        c = PACKAGE_CONFIG_CACHE.get(f'{__package__.partition(".")[0]}.marshal')
        assert c is not None
        assert c.codegen is True  # noqa

    for _ in range(2):
        assert PACKAGE_CONFIG_CACHE.get(f'{__package__.partition(".")[0]}.argparse') is None
