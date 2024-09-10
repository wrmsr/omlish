import dataclasses as dc
import typing as ta

from ... import lang
from .internals import FIELDS_ATTR
from .internals import PARAMS_ATTR
from .processing import Processor
from .reflect import ClassInfo
from .utils import Namespace
from .utils import create_fn
from .utils import set_new_attribute


if ta.TYPE_CHECKING:
    from . import metaclass
else:
    metaclass = lang.proxy_import('.metaclass', __package__)


def check_frozen_bases(info: ClassInfo) -> None:
    mc_base = getattr(metaclass, 'Data', None)
    all_frozen_bases = None
    any_frozen_base = False
    has_dataclass_bases = False
    for b in info.cls.__mro__[-1:0:-1]:
        if b is mc_base:
            continue
        base_fields = getattr(b, FIELDS_ATTR, None)
        if base_fields is not None:
            has_dataclass_bases = True
            if all_frozen_bases is None:
                all_frozen_bases = True
            current_frozen = getattr(b, PARAMS_ATTR).frozen
            all_frozen_bases = all_frozen_bases and current_frozen
            any_frozen_base = any_frozen_base or current_frozen

    if has_dataclass_bases:
        if any_frozen_base and not info.params.frozen:
            raise TypeError('cannot inherit non-frozen dataclass from a frozen one')

        if all_frozen_bases is False and info.params.frozen:
            raise TypeError('cannot inherit frozen dataclass from a non-frozen one')


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
    def check(self) -> None:
        check_frozen_bases(self._info)

    def _process(self) -> None:
        if not self._info.params.frozen:
            return

        for fn in frozen_get_del_attr(self._cls, self._info.instance_fields, self._info.globals):
            if set_new_attribute(self._cls, fn.__name__, fn):
                raise TypeError(f'Cannot overwrite attribute {fn.__name__} in class {self._cls.__name__}')
