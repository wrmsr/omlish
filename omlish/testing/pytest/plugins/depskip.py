"""
https://github.com/pytest-dev/pytest/blob/72c682ff9773ad2690711105a100423ebf7c7c15/src/_pytest/python.py#L494

--

https://github.com/pytest-dev/pytest-asyncio/blob/b1dc0c3e2e82750bdc6dbdf668d519aaa89c036c/pytest_asyncio/plugin.py#L657
"""
import dataclasses as dc
import re
import typing as ta

import pytest

from ._registry import register


@register
class DepSkipPlugin:
    @dc.dataclass(frozen=True)
    class Entry:
        file_pats: ta.Sequence[re.Pattern]
        imp_pats: ta.Sequence[re.Pattern]

    def __init__(self) -> None:
        super().__init__()

        self.entries: list[DepSkipPlugin.Entry] = []

    def should_skip(self, file_name: str, imp_name: str) -> bool:
        raise NotImplementedError

    @pytest.hookimpl
    def pytest_collectstart(self, collector: pytest.Collector) -> None:
        if isinstance(collector, pytest.Module):
            original_attr = f'__{self.__class__.__qualname__.replace(".", "__")}__original_getobj'

            def _patched_getobj():
                try:
                    return getattr(collector, original_attr)()
                except pytest.Collector.CollectError as ce:
                    if (oe := ce.__cause__) and isinstance(oe, ImportError):
                        file_name = collector.nodeid
                        imp_name = oe.name
                        if self.should_skip(file_name, imp_name):
                            pytest.skip(
                                f'skipping {file_name} to missing optional dependency {imp_name}',
                                allow_module_level=True,
                            )

                    raise

            setattr(collector, original_attr, collector._getobj)  # noqa
            collector._getobj = _patched_getobj  # type: ignore  # noqa
