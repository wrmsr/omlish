import dataclasses as dc
import reprlib
import typing as ta

from .processing import Processor
from .utils import Namespace
from .utils import create_fn
from .utils import set_new_attribute


def repr_fn(
        fields: ta.Sequence[dc.Field],
        globals: Namespace,
) -> ta.Callable:
    fn = create_fn(
        '__repr__',
        ('self',),
        [
            'return f"{self.__class__.__qualname__}(' +
            ', '.join([f"{f.name}={{self.{f.name}!r}}" for f in fields]) +
            ')"'
        ],
        globals=globals,
    )
    return reprlib.recursive_repr()(fn)


class ReprProcessor(Processor):
    def _process(self) -> None:
        if not self._info.params.repr:
            return

        flds = [f for f in self._info.instance_fields if f.repr]
        set_new_attribute(self._cls, '__repr__', repr_fn(flds, self._info.globals))  # noqa
