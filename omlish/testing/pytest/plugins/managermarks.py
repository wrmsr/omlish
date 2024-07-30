import abc
import contextlib
import typing as ta

import pytest

from .... import lang
from ._registry import register


class ManagerMark(lang.Abstract):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    @abc.abstractmethod
    def __call__(self, item: pytest.Function) -> ta.Iterator[None]:
        raise NotImplementedError


def _deep_subclasses(cls):
    ret = set()

    def rec(cur):
        for nxt in cur.__subclasses__():
            if nxt not in ret:
                ret.add(nxt)
                rec(nxt)

    rec(cls)
    return ret


@register
class ManagerMarksPlugin:

    @lang.cached_function
    def mark_classes(self) -> ta.Mapping[str, type[ManagerMark]]:
        return {
            cls.__name__: cls
            for cls in _deep_subclasses(ManagerMark)
            if not lang.is_abstract_class(cls)
        }

    def pytest_configure(self, config):
        for n in self.mark_classes():
            config.addinivalue_line(
                'markers',
                f'{n}: mark to manage {n}',
            )

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(self, item):
        with contextlib.ExitStack() as es:
            for n, cls in self.mark_classes().items():
                if (m := item.get_closest_marker(n)) is None:
                    continue
                inst = cls(*m.args, **m.kwargs)
                es.enter_context(contextlib.contextmanager(inst)(item))

            yield
