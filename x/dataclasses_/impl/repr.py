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
        *,
        repr_id: bool = False,
) -> ta.Callable:
    locals: dict[str, ta.Any] = {}  # noqa

    fields = sorted(fields, key=lambda f: get_field_extras(f).repr_priority or 0)

    prefix_src = '{self.__class__.__qualname__}'
    if repr_id:
        prefix_src += '@{hex(id(self))[2:]}'

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
            f'return f"{prefix_src}({{", ".join(l)}})"',
        ]

    else:
        src = [
            f'return f"{prefix_src}(' +
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
        rfn = repr_fn(flds, self._info.globals, repr_id=self._info.params_extras.repr_id)
        set_new_attribute(self._cls, '__repr__', rfn)  # noqa
