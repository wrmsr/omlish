"""
TODO:
 - ensure all 'init' fields work - non-instance
 - special case 'None' default, most common
"""
import dataclasses as dc
import typing as ta

from omlish import check

from ..generation.base import Generator
from ..generation.base import Plan
from ..generation.base import PlanResult
from ..generation.idents import FIELD_FN_VALIDATION_ERROR_IDENT
from ..generation.idents import FIELD_TYPE_VALIDATION_ERROR_IDENT
from ..generation.idents import FN_VALIDATION_ERROR_IDENT
from ..generation.idents import HAS_DEFAULT_FACTORY_IDENT
from ..generation.idents import ISINSTANCE_IDENT
from ..generation.idents import NONE_IDENT
from ..generation.idents import SELF_IDENT
from ..generation.ops import AddMethodOp
from ..generation.ops import Op
from ..generation.ops import OpRef
from ..generation.registry import register_generator_type
from ..generation.utils import SetattrSrcBuilder
from ..inspect import FieldsInspection
from ..processing.base import ProcessingContext
from ..specs import CoerceFn
from ..specs import DefaultFactory
from ..specs import FieldType
from ..specs import InitFn
from ..specs import ValidateFn
from ..std.internals import STD_POST_INIT_NAME
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

        check_type: OpRef[type | tuple[type, ...]] | None

    fields: tuple[Field, ...]

    frozen: bool

    post_init_params: tuple[str, ...] | None

    init_fns: tuple[OpRef[InitFn], ...]

    @dc.dataclass(frozen=True)
    class ValidateFnWithParams:
        fn: OpRef[ValidateFn]
        params: tuple[str, ...]

    validate_fns: ta.Sequence[ValidateFnWithParams] | None


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

        if ctx.cs.generic_init:
            gfad = ctx[FieldsInspection].generic_replaced_field_annotations
            get_ann = lambda f: gfad[f.name]
        else:
            get_ann = lambda f: f.annotation

        orm = {}

        bfs: list[InitPlan.Field] = []
        for i, f in enumerate(ctx.cs.fields):
            if not f.init:
                continue

            ar: OpRef = OpRef(f'init.fields.{i}.annotation')
            orm[ar] = get_ann(f)

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

            ctr: OpRef[type | tuple[type, ...]] | None = None
            if f.check_type is not None and f.check_type is not False:
                ct: ta.Any
                if isinstance(f.check_type, tuple):
                    ct = tuple(type(None) if e is None else check.isinstance(e, type) for e in f.check_type)
                elif isinstance(f.check_type, type):
                    ct = f.check_type
                elif f.check_type is True:
                    ct = f.annotation
                else:
                    raise TypeError(f.check_type)
                ctr = OpRef(f'init.fields.{i}.check_type')
                orm[ctr] = ct

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

                check_type=ctr,
            ))

        ifs: list[OpRef[InitFn]] = []
        for i, ifn in enumerate(ctx.cs.init_fns or []):
            ir: OpRef = OpRef(f'init.init_fns.{i}')
            orm[ir] = ifn
            ifs.append(ir)

        vfs: list[InitPlan.ValidateFnWithParams] = []
        for i, vfn in enumerate(ctx.cs.validate_fns or []):
            vfr: OpRef = OpRef(f'init.validate_fns.{i}')
            orm[vfr] = vfn.fn
            vfs.append(InitPlan.ValidateFnWithParams(
                fn=vfr,
                params=tuple(vfn.params),
            ))

        post_init_params: tuple[str, ...] | None = None
        if hasattr(ctx.cls, STD_POST_INIT_NAME):
            post_init_params = tuple(f.name for f in ctx[InitFields].all if f.field_type is FieldType.INIT)

        return PlanResult(
            InitPlan(
                fields=tuple(bfs),

                frozen=ctx.cs.frozen,

                post_init_params=post_init_params,

                init_fns=tuple(ifs),

                validate_fns=tuple(vfs),
            ),
            orm,
        )

    def generate(self, bs: InitPlan) -> ta.Iterable[Op]:
        ors: set[OpRef] = set()

        # proto

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

        # defaults

        for f in bs.fields:
            if f.default_factory is None:
                continue
            ors.add(f.default_factory)
            lines.extend([
                f'    if {f.name} is {HAS_DEFAULT_FACTORY_IDENT}:',
                f'        {f.name} = {f.default_factory.ident()}()',
            ])

        # coercion

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

        # validation

        for f in bs.fields:
            if f.check_type is None:
                continue
            ors.add(f.check_type)
            lines.extend([
                f'    if not {ISINSTANCE_IDENT}({f.name}, {f.check_type.ident()}): ',
                f'        raise {FIELD_TYPE_VALIDATION_ERROR_IDENT}(',
                f'            obj={SELF_IDENT},',
                f'            type={f.check_type.ident()},',
                f'            field={f.name!r},',
                f'            value={f.name},',
                f'        )',
            ])

        for f in bs.fields:
            if f.validate is None:
                continue
            ors.add(f.validate)
            lines.extend([
                f'    if not {f.validate.ident()}({f.name}): ',
                f'        raise {FIELD_FN_VALIDATION_ERROR_IDENT}(',
                f'            obj={SELF_IDENT},',
                f'            fn={f.validate.ident()},',
                f'            field={f.name!r},',
                f'            value={f.name},',
                f'        )',
            ])

        for vfn in bs.validate_fns or []:
            ors.add(vfn.fn)
            if vfn.params:
                lines.extend([
                    f'    if not {vfn.fn.ident()}(',
                    *[
                        f'        {p},'
                        for p in vfn.params
                    ],
                    f'    ):',
                ])
            else:
                lines.append(
                    f'    if not {vfn.fn.ident()}():',
                )
            lines.extend([
                f'        raise {FN_VALIDATION_ERROR_IDENT}(',
                f'            obj={SELF_IDENT},',
                f'            fn={vfn.fn.ident()},',
                f'        )',
            ])

        # setattr

        sab = SetattrSrcBuilder()
        for f in bs.fields:
            lines.extend([
                f'    {l}'
                for l in sab(f.name, f.name, frozen=bs.frozen, override=f.override)
            ])

        # post-init

        if (pia := bs.post_init_params) is not None:
            lines.append(
                f'    {SELF_IDENT}.{STD_POST_INIT_NAME}({", ".join(pia)})',
            )

        for ifn in bs.init_fns:
            ors.add(ifn)
            lines.append(
                f'    {ifn.ident()}({SELF_IDENT})',
            )

        #

        if not lines:
            lines.append(
                '    pass',
            )

        return [
            AddMethodOp('__init__', '\n'.join(lines), frozenset(ors)),
        ]
