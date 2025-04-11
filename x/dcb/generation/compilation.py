"""
TODO:
 - md5 spec to fn name
"""
import abc
import dataclasses as dc
import typing as ta

from omlish import check
from omlish.text.mangle import StringMangler

from ..utils import repr_round_trip_value
from .idents import CLS_IDENT
from .idents import FN_GLOBAL_IMPORTS
from .idents import FN_GLOBALS
from .idents import FUNCTION_TYPE_IDENT
from .idents import IDENT_PREFIX
from .idents import PROPERTY_IDENT
from .ops import AddMethodOp
from .ops import AddPropertyOp
from .ops import Op
from .ops import OpRef
from .ops import SetAttrOp
from .ops import get_op_refs


T = ta.TypeVar('T')


##


QUALNAME_MANGLER = StringMangler('_', '.')

COMPILED_FN_PREFIX = '_transform_dataclass__'


class OpCompiler:
    class Style(abc.ABC):
        @abc.abstractmethod
        def header_lines(self) -> ta.Sequence[str]:
            raise NotImplementedError

        @abc.abstractmethod
        def globals_ns(self) -> ta.Mapping[str, ta.Any]:
            raise NotImplementedError

    class JitStyle(Style):
        def header_lines(self) -> ta.Sequence[str]:
            return []

        def globals_ns(self) -> ta.Mapping[str, ta.Any]:
            return dict(FN_GLOBAL_IMPORTS)

    class AotStyle(Style):
        HEADER_LINES: ta.ClassVar[ta.Sequence[str]] = [
            '# type: ignore',
            '# ruff: noqa',
            '# flake8: noqa',
            '# @omlish-generated',
        ]

        def header_lines(self) -> ta.Sequence[str]:
            return [
                *self.HEADER_LINES,
                *[
                    f'import {i}'
                    for i in FN_GLOBAL_IMPORTS
                ],
                '',
                '',
            ]

        def globals_ns(self) -> ta.Mapping[str, ta.Any]:
            return {}

    #

    def __init__(
            self,
            qualname: str,
            style: Style,
    ) -> None:
        super().__init__()

        self._qualname = qualname
        self._mangled_qualname = QUALNAME_MANGLER.mangle(qualname)
        self._style = style

    @property
    def style(self) -> Style:
        return self._style

    @dc.dataclass(frozen=True)
    class CompileResult:
        fn_name: str
        params: ta.Sequence[str]
        src: str
        refs: frozenset[OpRef]

    @dc.dataclass(frozen=True)
    class _FnParam:
        name: str
        src: str | None = None
        noqa: bool = dc.field(default=False, kw_only=True)

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

        params: list[OpCompiler._FnParam] = [
            OpCompiler._FnParam(CLS_IDENT),
            *[OpCompiler._FnParam(p) for p in sorted(r.ident() for r in refs)],
        ]

        params.extend([
            OpCompiler._FnParam(
                k,
                src=f'{k}={v.src}' if not v.src.startswith('.') else k,
                noqa=k != k.lower() or not v.src.startswith('.'),
            )
            for k, v in FN_GLOBALS.items()
        ])

        fn_name = f'{COMPILED_FN_PREFIX}{self._mangled_qualname}'

        lines: list[str] = []

        lines.extend(self._style.header_lines())

        lines.extend([
            f'def {fn_name}(',
            f'    *,',
            *[
                f'    {p.src if p.src is not None else p.name},{"  # noqa" if p.noqa  else ""}'
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
            [p.name for p in params],
            src,
            refs,
        )
