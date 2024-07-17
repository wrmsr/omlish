import dataclasses as dc
import reprlib
import typing as ta

from .params import get_field_extras
from .processing import Processor
from .utils import Namespace
from .utils import create_fn
from .utils import set_new_attribute


def repr_fn(
        fields: ta.Sequence[dc.Field],
        globals: Namespace,  # noqa
) -> ta.Callable:
    locals: dict[str, ta.Any] = {}  # noqa
    if any(get_field_extras(f).repr_fn is not None for f in fields):
        lst: list[str] = []
        for f in fields:
            if (fex := get_field_extras(f)).repr_fn is not None:
                locals[fn_name := f'__repr_fn__{f.name}'] = fex.repr_fn
                lst.append(f"if (r := {fn_name}(self.{f.name})) is not None: l.append(f'{f.name}={{r}}')")
            else:
                lst.append(f"l.append(f'{f.name}={{self.{f.name}!r}}')")
        src = [
            'l = []',
            *lst,
            'return f"{self.__class__.__qualname__}({", ".join(l)})"',
        ]
    else:
        src = [
            'return f"{self.__class__.__qualname__}(' +
            ', '.join([f'{f.name}={{self.{f.name}!r}}' for f in fields]) +
            ')"',
        ]
    fn = create_fn(
        '__repr__',
        ('self',),
        src,
        globals=globals,
        locals=locals,
    )
    return reprlib.recursive_repr()(fn)


class ReprProcessor(Processor):
    def _process(self) -> None:
        if not self._info.params.repr:
            return

        flds = [f for f in self._info.instance_fields if f.repr]
        set_new_attribute(self._cls, '__repr__', repr_fn(flds, self._info.globals))  # noqa
