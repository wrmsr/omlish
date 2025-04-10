"""
TODO:
 - special case 'None' default, most common
"""
import dataclasses as dc
import typing as ta

from omlish import check

from ..generation.base import Generator
from ..generation.base import Plan
from ..generation.base import PlanResult
from ..generation.idents import FIELD_VALIDATION_ERROR_IDENT
from ..generation.idents import HAS_DEFAULT_FACTORY_IDENT
from ..generation.idents import NONE_IDENT
from ..generation.idents import SELF_IDENT
from ..generation.ops import AddMethodOp
from ..generation.ops import Op
from ..generation.ops import OpRef
from ..generation.registry import register_generator_type
from ..generation.utils import SetattrSrcBuilder
from ..processing import ProcessingContext
from ..specs import FieldType
from ..types import CoerceFn
from ..types import DefaultFactory
from ..types import InitFn
from ..types import ValidateFn
from .fields import InitFields


##


@dc.dataclass(frozen=True, kw_only=True)
class InitPlan(Plan):
    @dc.dataclass(frozen=True)
    class Field:
        name: str
        annotation: OpRef[ta.Any]

        default: OpRef[ta.Any] | None
        default_factory: OpRef[ta.Any] | None

        kw_only: bool

        override: bool

        field_type: FieldType

        coerce: bool | OpRef[CoerceFn] | None
        validate: OpRef[ValidateFn] | None

    fields: tuple[Field, ...]

    frozen: bool

    init_fns: tuple[OpRef[InitFn], ...]


@register_generator_type(InitPlan)
class InitGenerator(Generator[InitPlan]):
    def plan(self, ctx: ProcessingContext) -> PlanResult[InitPlan] | None:
        if '__init__' in ctx.cls.__dict__:
            return None

        seen_default = None
        for f in ctx[InitFields].std:
            if not f.init:
                continue
            if f.default.present:
                seen_default = f
            elif seen_default:
                raise TypeError(f'non-default argument {f.name!r} follows default argument {seen_default.name!r}')

        orm = {}

        bfs: list[InitPlan.Field] = []
        for i, f in enumerate(ctx.cs.fields):
            if not f.init:
                continue

            ar: OpRef = OpRef(f'init.fields.{i}.annotation')
            orm[ar] = f.annotation

            dr: OpRef[ta.Any] | None = None
            dfr: OpRef[ta.Any] | None = None
            if f.default.present:
                dfl = f.default.must()
                if isinstance(dfl, DefaultFactory):
                    dfr = OpRef(f'init.fields.{i}.default_factory')
                    orm[dfr] = dfl.fn
                else:
                    dr = OpRef(f'init.fields.{i}.default')
                    orm[dr] = dfl

            co: bool | OpRef[CoerceFn] | None = None
            if isinstance(f.coerce, bool):
                co = f.coerce
            elif f.coerce is not None:
                co = OpRef(f'init.fields.{i}.coerce')
                orm[co] = f.coerce

            vr: OpRef[ValidateFn] | None = None
            if f.validate is not None:
                vr = OpRef(f'init.fields.{i}.validate')
                orm[vr] = f.validate

            bfs.append(InitPlan.Field(
                name=f.name,
                annotation=ar,

                default=dr,
                default_factory=dfr,

                kw_only=f.kw_only,

                override=f.override or ctx.cs.override,

                field_type=f.field_type,

                coerce=co,
                validate=vr,
            ))

        ifs: list[OpRef[InitFn]] = []
        for i, ifn in enumerate(ctx.cs.init_fns or []):
            ir: OpRef = OpRef(f'init.init_fns.{i}')
            orm[ir] = ifn
            ifs.append(ir)

        return PlanResult(
            InitPlan(
                fields=tuple(bfs),
                frozen=ctx.cs.frozen,
                init_fns=tuple(ifs),
            ),
            orm,
        )

    def generate(self, bs: InitPlan) -> ta.Iterable[Op]:
        ors: set[OpRef] = set()

        params: list[str] = []
        seen_kw_only = False
        for f in bs.fields:
            if f.kw_only:
                if not seen_kw_only:
                    params.append('*')
                    seen_kw_only = True
            elif seen_kw_only:
                raise TypeError(f'non-keyword-only argument {f.name!r} follows keyword-only argument(s)')

            ors.add(f.annotation)
            p = f'{f.name}: {f.annotation.ident()}'

            if f.default_factory is not None:
                check.none(f.default)
                p += f' = {HAS_DEFAULT_FACTORY_IDENT}'
            elif f.default is not None:
                check.none(f.default_factory)
                ors.add(f.default)
                p += f' = {f.default.ident()}'

            params.append(p)

        lines = [
            f'def __init__(',
            f'    {SELF_IDENT},',
            *[
                f'    {p},'
                for p in params
            ],
            f') -> {NONE_IDENT}:',
        ]

        for f in bs.fields:
            if f.default_factory is None:
                continue
            ors.add(f.default_factory)
            lines.extend([
                f'    if {f.name} is {HAS_DEFAULT_FACTORY_IDENT}:',
                f'        {f.name} = {f.default_factory.ident()}()',
            ])

        for f in bs.fields:
            if isinstance(f.coerce, bool) and f.coerce:
                lines.append(
                    f'    {f.name} = {f.annotation.ident()}({f.name})',
                )
            elif isinstance(f.coerce, OpRef):
                ors.add(f.coerce)
                lines.append(
                    f'    {f.name} = {f.coerce.ident()}({f.name})',
                )

        for f in bs.fields:
            if f.validate is None:
                continue
            ors.add(f.validate)
            lines.extend([
                f'    if not {f.validate.ident()}({f.name}): ',
                f'        raise {FIELD_VALIDATION_ERROR_IDENT}(',
                f'            {SELF_IDENT},',
                f'            {f.name!r},',
                f'            {f.validate.ident()},',
                f'            {f.name},',
                f'        )',
            ])

        sab = SetattrSrcBuilder()
        for f in bs.fields:
            lines.extend([
                f'    {l}'
                for l in sab(f.name, f.name, frozen=bs.frozen, override=f.override)
            ])

        for ifn in bs.init_fns:
            ors.add(ifn)
            lines.append(
                f'    {ifn.ident()}({SELF_IDENT})',
            )

        if not bs.fields:
            lines.append(
                '    pass',
            )

        return [
            AddMethodOp('__init__', '\n'.join(lines), frozenset(ors)),
        ]
