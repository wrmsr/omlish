import gc
import typing as ta

import pytest

from .plugins.managermarks import ManagerMark


##


class gc_collect_after(ManagerMark):  # noqa
    def __call__(self, item: pytest.Function) -> ta.Iterator[None]:
        try:
            yield
        finally:
            gc.collect()
