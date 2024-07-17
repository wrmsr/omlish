import dataclasses as dc
import typing as ta

from .processing import Processor
from .utils import Namespace
from .utils import create_fn
from .utils import set_new_attribute


def frozen_get_del_attr(
        cls: type,
        fields: ta.Sequence[dc.Field],
        globals: Namespace,  # noqa
) -> tuple[ta.Callable, ta.Callable]:
    locals = {  # noqa
        'cls': cls,
        'FrozenInstanceError': dc.FrozenInstanceError,
    }
    condition = 'type(self) is cls'
    if fields:
        condition += ' or name in {' + ', '.join(repr(f.name) for f in fields) + '}'
    return (
        create_fn(
            '__setattr__',
            ('self', 'name', 'value'),
            [
                f'if {condition}:',
                ' raise FrozenInstanceError(f"cannot assign to field {name!r}")',
                f'super(cls, self).__setattr__(name, value)',
            ],
            locals=locals,
            globals=globals,
        ),
        create_fn(
            '__delattr__',
            ('self', 'name'),
            [
                f'if {condition}:',
                ' raise FrozenInstanceError(f"cannot delete field {name!r}")',
                f'super(cls, self).__delattr__(name)',
            ],
            locals=locals,
            globals=globals,
        ),
    )


class FrozenProcessor(Processor):
    def _process(self) -> None:
        if not self._info.params.frozen:
            return

        for fn in frozen_get_del_attr(self._cls, self._info.instance_fields, self._info.globals):
            if set_new_attribute(self._cls, fn.__name__, fn):
                raise TypeError(f'Cannot overwrite attribute {fn.__name__} in class {self._cls.__name__}')
