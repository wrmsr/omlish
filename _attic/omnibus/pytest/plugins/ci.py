import pytest

from ._registry import register_plugin


_CI = None


def set_ci(value: bool) -> None:
    global _CI
    if _CI is not None:
        raise ValueError
    if not isinstance(value, bool):
        raise TypeError(value)
    _CI = value


def is_ci() -> bool:
    global _CI
    if _CI is None:
        _CI = False
    return bool(_CI)


def skip_if_ci() -> None:
    if is_ci():
        pytest.skip(f'ci disabled')


@register_plugin
class CiPlugin:

    def pytest_addoption(self, parser):
        parser.addoption('--ci', action='store_true', default=False, help=f'toggle ci mode')

    def pytest_collection(self, session: pytest.Session):
        global _CI
        if _CI is None:
            _CI = bool(session.config.getoption('--ci'))

    def pytest_collection_modifyitems(self, config, items):
        if not _CI:
            return
        skip = pytest.mark.skip(reason='omit --ci to run')
        for item in items:
            if 'no_ci' in item.keywords:
                item.add_marker(skip)

    def pytest_configure(self, config):
        config.addinivalue_line('markers', 'no_ci: mark test as disabled in ci')
