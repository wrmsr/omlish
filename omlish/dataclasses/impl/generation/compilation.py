"""
TODO:
 - md5 spec to fn name
"""
import abc
import dataclasses as dc
import typing as ta

from .... import check
from .... import lang
from ..utils import repr_round_trip_value
from .globals import FN_GLOBAL_IMPORTS
from .globals import FN_GLOBALS
from .globals import FUNCTION_TYPE_GLOBAL
from .globals import PROPERTY_GLOBAL
from .globals import TYPE_ERROR_GLOBAL
from .idents import CLS_IDENT
from .idents import IDENT_PREFIX
from .ops import AddMethodOp
from .ops import AddPropertyOp
from .ops import IfAttrPresent
from .ops import Op
from .ops import OpRef
from .ops import Ref
from .ops import SetAttrOp
from .ops import get_op_refs


T = ta.TypeVar('T')


##


class OpCompiler:
    class Style(lang.Abstract):
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
                '\n',
            ]

        def globals_ns(self) -> ta.Mapping[str, ta.Any]:
            return {}

    #

    def __init__(
            self,
            style: Style,
    ) -> None:
        super().__init__()

        self._style = style

    @property
    def style(self) -> Style:
        return self._style

    @dc.dataclass(frozen=True)
    class CompileResult:
        fn_name: str
        params: ta.Sequence[str]
        src: str
        refs: frozenset[Ref]

    @dc.dataclass(frozen=True)
    class _FnParam:
        name: str
        src: str | None = None
        noqa: bool = dc.field(default=False, kw_only=True)

    def _compile_set_attr(
            self,
            attr_name: str,
            value_src: str,
            if_present: IfAttrPresent,
    ) -> list[str]:
        setattr_stmt = f'setattr({CLS_IDENT}, {attr_name!r}, {value_src})'

        if if_present == 'skip':
            return [
                f'if {attr_name!r} not in {CLS_IDENT}.__dict__:',
                f'    {setattr_stmt}',
            ]

        elif if_present == 'replace':
            return [
                setattr_stmt,
            ]

        elif if_present == 'error':
            return [
                f'if {attr_name!r} in {CLS_IDENT}.__dict__:',
                (
                    f'    '
                    f'raise {TYPE_ERROR_GLOBAL.ident}'
                    f'(f"Cannot overwrite attribute {attr_name} in class {{{CLS_IDENT}.__name__}}")'
                ),
                setattr_stmt,
            ]

        else:
            raise ValueError(if_present)

    def compile(
            self,
            fn_name: str,
            ops: ta.Sequence[Op],
    ) -> CompileResult:
        body_lines: list[str] = []

        for op in ops:
            if isinstance(op, SetAttrOp):
                if isinstance(v := op.value, OpRef):
                    vs = v.ident()
                    body_lines.extend([
                        f'if isinstance({vs}, {FUNCTION_TYPE_GLOBAL.ident}):'
                        f'    {vs}.__qualname__ = f"{{{CLS_IDENT}.__qualname__}}.{{{vs}.__name__}}"',
                    ])
                else:
                    vs = repr(repr_round_trip_value(v))

                body_lines.extend(self._compile_set_attr(
                    op.name,
                    vs,
                    op.if_present,
                ))

            elif isinstance(op, AddMethodOp):
                body_lines.extend([
                    *op.src.splitlines(),
                    f'',
                    f'{op.name}.__qualname__ = f"{{{CLS_IDENT}.__qualname__}}.{op.name}"',
                    *self._compile_set_attr(
                        op.name,
                        op.name,
                        op.if_present,
                    ),
                ])

            elif isinstance(op, AddPropertyOp):
                gen_ident = IDENT_PREFIX + f'property__{op.name}'

                gen_lines = [
                    f'def {gen_ident}():',
                    f'    @{PROPERTY_GLOBAL.ident}',
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
                    f'',
                    f'setattr({CLS_IDENT}, {op.name!r}, {gen_ident}())',
                ])

            else:
                raise TypeError(op)

            body_lines.append('')

        #

        refs = frozenset.union(*[get_op_refs(o) for o in ops])

        params: list[OpCompiler._FnParam] = [
            OpCompiler._FnParam(CLS_IDENT),
            *[
                OpCompiler._FnParam(p)
                for p in sorted(
                    r.ident()
                    for r in refs
                    if isinstance(r, OpRef)
                )
            ],
        ]

        params.extend([
            OpCompiler._FnParam(
                k.ident,
                src=f'{k.ident}={v.src}' if not v.src.startswith('.') else k.ident,
                noqa=k.ident != k.ident.lower() or not v.src.startswith('.'),
            )
            for k, v in FN_GLOBALS.items()
        ])

        lines: list[str] = []

        lines.extend(self._style.header_lines())

        lines.extend([
            f'def {fn_name}(',
            f'    *,',
            *[
                f'    {p.src if p.src is not None else p.name},{"  # noqa" if p.noqa else ""}'
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
