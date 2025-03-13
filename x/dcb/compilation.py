import typing as ta

from omlish.text.mangle import StringMangler

from .idents import CLS_IDENT
from .idents import FN_GLOBALS
from .ops import AddMethodOp
from .ops import Op
from .ops import SetAttrOp


T = ta.TypeVar('T')


##


QUALNAME_MANGLER = StringMangler('_', '.')

COMPILED_FN_PREFIX = '__transform_dataclass__'


class OpCompiler:
    def __init__(self, qualname: str) -> None:
        super().__init__()

        self._qualname = qualname
        self._mangled_qualname = QUALNAME_MANGLER.mangle(qualname)

    def compile(self, ops: ta.Sequence[Op]) -> str:
        body_lines: list[str] = []

        for op in ops:
            if isinstance(op, SetAttrOp):
                # set_qualname(self._cls, op.value)  # FIXME
                setattr_stmt = f'setattr({CLS_IDENT}, {op.name!r}, {op.value!r})'  # FIXME: repr??
                if op.if_present == 'skip':
                    body_lines.extend([
                        f'if {op.name!r} not in {CLS_IDENT}.__dict__:',
                        f'    {setattr_stmt}',
                    ])
                elif op.if_present == 'replace':
                    body_lines.append(
                        setattr_stmt,
                    )
                elif op.if_present == 'raise':
                    body_lines.extend([
                        f'if {op.name!r} in {CLS_IDENT}.__dict__:',
                        f'    raise AttributeError({op.name!r})',
                        setattr_stmt,
                    ])
                else:
                    raise ValueError(op.if_present)

            elif isinstance(op, AddMethodOp):
                body_lines.extend([
                    *op.src.splitlines(),
                    '',
                    f'{op.name}.__qualname__ = f"{{{CLS_IDENT}.__qualname__}}.{op.name}"',
                    f'setattr({CLS_IDENT}, {op.name!r}, {op.name})',
                ])

            else:
                raise TypeError(op)

            body_lines.append('')

        #

        refs = {r for o in ops if isinstance(o, AddMethodOp) for r in o.refs}

        params = [
            *sorted(r.ident() for r in refs),
            *FN_GLOBALS,
        ]

        fn_name = f'{COMPILED_FN_PREFIX}{self._mangled_qualname}'

        lines = [
            f'def {fn_name}(',
            f'    *',
            *[
                f'    {p},'
                for p in params
            ],
            f'):',
            *[
                f'    {l}'
                for l in body_lines
            ],
        ]

        #

        src = '\n'.join(lines)

        return src
