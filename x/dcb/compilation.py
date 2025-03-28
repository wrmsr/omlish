import dataclasses as dc
import typing as ta

from omlish import check
from omlish.text.mangle import StringMangler

from .idents import CLS_IDENT
from .idents import FN_GLOBALS
from .idents import FN_GLOBAL_IMPORTS
from .idents import FUNCTION_TYPE_IDENT
from .idents import IDENT_PREFIX
from .idents import PROPERTY_IDENT
from .ops import AddMethodOp
from .ops import AddPropertyOp
from .ops import Op
from .ops import OpRef
from .ops import SetAttrOp
from .ops import get_op_refs
from .utils import repr_round_trip_value


T = ta.TypeVar('T')


##


QUALNAME_MANGLER = StringMangler('_', '.')

COMPILED_FN_PREFIX = '_transform_dataclass__'


class OpCompiler:
    def __init__(
            self,
            qualname: str,
            *,
            set_global_kwarg_defaults: bool = False,
            import_global_modules: bool = False,
    ) -> None:
        super().__init__()

        self._qualname = qualname
        self._mangled_qualname = QUALNAME_MANGLER.mangle(qualname)

        self._set_global_kwarg_defaults = set_global_kwarg_defaults
        self._import_global_modules = import_global_modules

    @dc.dataclass(frozen=True)
    class CompileResult:
        fn_name: str
        params: ta.Sequence[str]
        src: str
        refs: frozenset[OpRef]

    def compile(self, ops: ta.Sequence[Op]) -> CompileResult:
        body_lines: list[str] = []

        for op in ops:
            if isinstance(op, SetAttrOp):
                if isinstance(v := op.value, OpRef):
                    vs = v.ident()
                    body_lines.extend([
                        f'if isinstance({vs}, {FUNCTION_TYPE_IDENT}):'
                        f'    {vs}.__qualname__ = f"{{{CLS_IDENT}.__qualname__}}.{{{vs}.__name__}}"',
                    ])
                else:
                    vs = repr(repr_round_trip_value(v))

                setattr_stmt = f'setattr({CLS_IDENT}, {op.name!r}, {vs})'

                if op.if_present == 'skip':
                    body_lines.extend([
                        f'if {op.name!r} not in {CLS_IDENT}.__dict__:',
                        f'    {setattr_stmt}',
                    ])
                elif op.if_present == 'replace':
                    body_lines.append(
                        setattr_stmt,
                    )
                elif op.if_present == 'error':
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
                    f'if {op.name!r} in {CLS_IDENT}.__dict__:',
                    f'    raise AttributeError({op.name!r})',
                    f'setattr({CLS_IDENT}, {op.name!r}, {op.name})',
                ])

            elif isinstance(op, AddPropertyOp):
                gen_ident = IDENT_PREFIX + f'property__{op.name}'

                gen_lines = [
                    f'def {gen_ident}():',
                    f'    @{PROPERTY_IDENT}',
                    *[
                        f'    {l}'
                        for l in check.not_none(op.get_src).splitlines()
                    ],
                ]
                if op.set_src is not None:
                    gen_lines.extend([
                        f'',
                        f'    @{op.name}.setter',
                        *[
                            f'    {l}'
                            for l in op.set_src.splitlines()
                        ],
                    ])
                if op.del_src is not None:
                    raise NotImplementedError
                gen_lines.extend([
                    f'',
                    f'    return {op.name}',
                ])

                body_lines.extend([
                    *gen_lines,
                    '',
                    f'setattr({CLS_IDENT}, {op.name!r}, {gen_ident}())',
                ])

            else:
                raise TypeError(op)

            body_lines.append('')

        #

        refs = frozenset.union(*[get_op_refs(o) for o in ops])

        params = [
            CLS_IDENT,
            *sorted(r.ident() for r in refs),
        ]

        if self._set_global_kwarg_defaults:
            params.extend([f'{k}={v.src}' for k, v in FN_GLOBALS.items()])
        else:
            params.extend(FN_GLOBALS)

        fn_name = f'{COMPILED_FN_PREFIX}{self._mangled_qualname}'

        lines = []

        if self._import_global_modules:
            lines.extend([
                *[
                    f'import {i}'
                    for i in FN_GLOBAL_IMPORTS
                ],
                '',
                '',
            ])

        lines.extend([
            f'def {fn_name}(',
            f'    *,',
            *[
                f'    {p},'
                for p in params
            ],
            f'):',
            *[
                f'    {l}'
                for l in body_lines
            ],
        ])

        #

        src = '\n'.join(lines)

        return self.CompileResult(
            fn_name,
            params,
            src,
            refs,
        )
