import typing as ta

from .utils import Namespace
from .processing import Processor
from .utils import create_fn
from .utils import set_new_attribute
from .utils import tuple_str


def cmp_fn(
        name: str,
        op: str,
        self_tuple: str,
        other_tuple: str,
        globals: Namespace,
) -> ta.Callable:
    return create_fn(
        name,
        ('self', 'other'),
        [
            'if other.__class__ is self.__class__:',
            f' return {self_tuple}{op}{other_tuple}',
            'return NotImplemented',
        ],
        globals=globals,
    )


class OrderProcessor(Processor):
    def _process(self) -> None:
        if not self._info.params.order:
            return

        flds = [f for f in self._info.instance_fields if f.compare]
        self_tuple = tuple_str('self', flds)
        other_tuple = tuple_str('other', flds)
        for name, op in [
            ('__lt__', '<'),
            ('__le__', '<='),
            ('__gt__', '>'),
            ('__ge__', '>='),
        ]:
            if set_new_attribute(self._cls, name, cmp_fn(name, op, self_tuple, other_tuple, globals=self._info.globals)):  # noqa
                raise TypeError(
                    f'Cannot overwrite attribute {name} in class {self._cls.__name__}. '
                    f'Consider using functools.total_ordering'
                )
