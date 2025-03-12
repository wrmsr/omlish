"""
TODO:
 - go-style tags: +slow,-ci, ...
"""
from _pytest.main import resolve_collection_argument  # noqa
import pytest

from ._registry import register


@register
class SkipsPlugin:
    def pytest_collection_modifyitems(self, session, items):
        dct: dict[str, set[str]] = {}
        for arg in session.config.args:
            ca = resolve_collection_argument(
                session.config.invocation_params.dir,
                arg,
                as_pypath=session.config.option.pyargs,
            )
            if ca.path.is_file():
                dct.setdefault(ca.path.as_posix(), set()).update(ca.parts)

        skip = pytest.mark.skip(reason='skipped (not specified alone)')
        for item in items:
            if 'skip_unless_alone' in item.keywords:
                if item.name not in dct.get(item.fspath.strpath, ()):
                    item.add_marker(skip)

    def pytest_configure(self, config):
        config.addinivalue_line('markers', 'skip_unless_alone: mark test as skipped unless specified alone')
