"""
https://github.com/pytest-dev/pytest/blob/72c682ff9773ad2690711105a100423ebf7c7c15/src/_pytest/python.py#L494

--

https://github.com/pytest-dev/pytest-asyncio/blob/b1dc0c3e2e82750bdc6dbdf668d519aaa89c036c/pytest_asyncio/plugin.py#L657
"""
import dataclasses as dc
import re
import typing as ta

import pytest

from .... import check
from ._registry import register as register_plugin
from .utils import find_plugin


##


@register_plugin
class DepSkipPlugin:
    @dc.dataclass(frozen=True)
    class Entry:
        file_pats: ta.Sequence[re.Pattern]
        imp_pats: ta.Sequence[re.Pattern]

    def __init__(self) -> None:
        super().__init__()

        self._entries: list[DepSkipPlugin.Entry] = []

    def add_entry(self, e: Entry) -> None:
        self._entries.append(e)

    def should_skip(self, file_name: str, imp_name: str) -> bool:
        for e in self._entries:
            if (
                any(fp.fullmatch(file_name) for fp in e.file_pats) and
                any(ip.fullmatch(imp_name) for ip in e.imp_pats)
            ):
                return True
        return False

    @pytest.hookimpl
    def pytest_collectstart(self, collector: pytest.Collector) -> None:
        if isinstance(collector, pytest.Module):
            original_attr = f'__{self.__class__.__qualname__.replace(".", "__")}__original_getobj'

            def _patched_getobj():
                try:
                    return getattr(collector, original_attr)()
                except pytest.Collector.CollectError as ce:
                    if (oe := ce.__cause__) and isinstance(oe, ImportError):
                        if (
                                (file_name := collector.nodeid) and
                                (imp_name := oe.name) and
                                self.should_skip(file_name, imp_name)  # noqa
                        ):
                            pytest.skip(
                                f'skipping {file_name} to missing optional dependency {imp_name}',
                                allow_module_level=True,
                            )

                    raise

            setattr(collector, original_attr, collector._getobj)  # noqa
            collector._getobj = _patched_getobj  # type: ignore  # noqa


def regex_register(
        pm: pytest.PytestPluginManager,
        file_pats: ta.Iterable[str],
        imp_pats: ta.Iterable[str],
) -> None:
    check.not_isinstance(file_pats, str)
    check.not_isinstance(imp_pats, str)

    pg = check.not_none(find_plugin(pm, DepSkipPlugin))
    pg.add_entry(DepSkipPlugin.Entry(
        [re.compile(fp) for fp in file_pats],
        [re.compile(ip) for ip in imp_pats],
    ))


def module_register(
        pm: pytest.PytestPluginManager,
        mods: ta.Iterable[str],
        imp_mods: ta.Iterable[str],
) -> None:
    check.not_isinstance(mods, str)
    check.not_isinstance(imp_mods, str)

    for m in [*mods, *imp_mods]:
        check.non_empty_str(m)
        check.arg(all(p.isidentifier() for p in m.split('.')), m)

    regex_register(
        pm,
        [rf'{re.escape(m.replace(".", "/"))}(/.*)?\.py' for m in mods],
        [rf'{re.escape(m.replace(".", "/"))}(\..*)?' for m in imp_mods],
    )
