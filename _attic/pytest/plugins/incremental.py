import typing as ta

import pytest

from ._registry import register_plugin


_FAILED_INCREMENTAL: ta.Dict[str, ta.Dict[ta.Tuple[int, ...], str]] = {}


@register_plugin
class IncrementalPlugin:

    def pytest_runtest_makereport(self, item, call):
        if 'incremental' not in item.keywords:
            return

        if call.excinfo is None:
            return

        cls_name = str(item.cls)
        parametrize_index = tuple(item.callspec.indices.values()) if hasattr(item, 'callspec') else ()
        test_name = item.originalname or item.name
        _FAILED_INCREMENTAL.setdefault(cls_name, {}).setdefault(parametrize_index, test_name)

    def pytest_runtest_setup(self, item):
        if 'incremental' not in item.keywords:
            return

        cls_name = str(item.cls)
        if cls_name not in _FAILED_INCREMENTAL:
            return

        parametrize_index = tuple(item.callspec.indices.values()) if hasattr(item, 'callspec') else ()
        test_name = _FAILED_INCREMENTAL[cls_name].get(parametrize_index, None)
        if test_name is not None:
            pytest.xfail('previous test failed ({})'.format(test_name))
