"""
TODO:
 - special case 'None' default, most common
"""
import dataclasses as dc
import typing as ta

from omlish import check

from ..generators.base import Generator
from ..generators.base import Plan
from ..generators.base import PlanContext
from ..generators.base import PlanResult
from ..generators.registry import register_generator_type
from ..generators.utils import build_setattr_src
from ..idents import NONE_IDENT
from ..idents import SELF_IDENT
from ..ops import AddMethodOp
from ..ops import Op
from ..ops import OpRef
from ..types import DefaultFactory
from ..types import InitFn


##


@dc.dataclass(frozen=True, kw_only=True)
class InitPlan(Plan):
    @dc.dataclass(frozen=True)
    class Field:
        name: str
        annotation: OpRef[ta.Any]

        default: OpRef[ta.Any] | None
        default_factory: OpRef[ta.Any] | None

        override: bool

    fields: tuple[Field, ...]

    frozen: bool

    init_fns: tuple[OpRef[InitFn], ...]


@register_generator_type(InitPlan)
class InitGenerator(Generator[InitPlan]):
    def plan(self, ctx: PlanContext) -> PlanResult[InitPlan] | None:
        if '__init__' in ctx.cls.__dict__:
            return None

        orm = {}

        bfs: list[InitPlan.Field] = []
        for i, f in enumerate(ctx.cs.fields):
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

            bfs.append(InitPlan.Field(
                name=f.name,
                annotation=ar,

                default=dr,
                default_factory=dfr,

                override=f.override or ctx.cs.override,
            ))

        ifs: list[OpRef[InitFn]] = []
        for i, ifn in enumerate(ctx.cs.init_fns or []):
            ir = OpRef(f'init.init_fns.{i}')
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
        for f in bs.fields:
            p = f'{f.name}: {f.annotation.ident()}'
            ors.add(f.annotation)

            if f.default_factory is not None:
                check.none(f.default)
                raise NotImplementedError
            elif f.default is not None:
                check.none(f.default_factory)
                raise NotImplementedError

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
            lines.append(f'    {build_setattr_src(f.name, f.name, frozen=bs.frozen, override=f.override)}')

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
