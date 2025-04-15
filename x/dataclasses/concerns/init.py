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
from ..internals import STD_POST_INIT_NAME
from ..processing.base import ProcessingContext
from ..specs import CoerceFn
from ..specs import DefaultFactory
from ..specs import FieldSpec
from ..specs import FieldType
from ..specs import InitFn
from ..specs import ValidateFn
from .fields import InitFields
from .mro import MroDict


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

    self_param: str
    std_params: tuple[str, ...]
    kw_only_params: tuple[str, ...]

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
    def _plan_field(
            self,
            ctx: ProcessingContext,
            i: int,
            f: FieldSpec,
            ann: ta.Any,
            ref_map: dict,
    ) -> InitPlan.Field:
        ann_ref: OpRef = OpRef(f'init.fields.{i}.annotation')
        ref_map[ann_ref] = ann

        default_ref: OpRef[ta.Any] | None = None
        default_factory_ref: OpRef[ta.Any] | None = None
        if f.default.present:
            dfl = f.default.must()
            if isinstance(dfl, DefaultFactory):
                default_factory_ref = OpRef(f'init.fields.{i}.default_factory')
                ref_map[default_factory_ref] = dfl.fn
            else:
                default_ref = OpRef(f'init.fields.{i}.default')
                ref_map[default_ref] = dfl

        coerce: bool | OpRef[CoerceFn] | None = None
        if isinstance(f.coerce, bool):
            coerce = f.coerce
        elif f.coerce is not None:
            coerce = OpRef(f'init.fields.{i}.coerce')
            ref_map[coerce] = f.coerce

        validate_ref: OpRef[ValidateFn] | None = None
        if f.validate is not None:
            validate_ref = OpRef(f'init.fields.{i}.validate')
            ref_map[validate_ref] = f.validate

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
            ref_map[ctr] = ct

        return InitPlan.Field(
            name=f.name,
            annotation=ann_ref,

            default=default_ref,
            default_factory=default_factory_ref,

            kw_only=f.kw_only,

            override=f.override or ctx.cs.override,

            field_type=f.field_type,

            coerce=coerce,
            validate=validate_ref,

            check_type=ctr,
        )

    def plan(self, ctx: ProcessingContext) -> PlanResult[InitPlan] | None:
        if '__init__' in ctx.cls.__dict__:
            return None

        init_fields = ctx[InitFields]
        seen_default = None
        for f in init_fields.std:
            if not f.init:
                continue
            if f.default.present:
                seen_default = f
            elif seen_default:
                raise TypeError(f'non-default argument {f.name!r} follows default argument {seen_default.name!r}')

        if ctx.cs.generic_init:
            gr_field_anns = ctx[FieldsInspection].generic_replaced_field_annotations
            get_field_ann = lambda f: gr_field_anns[f.name]
        else:
            get_field_ann = lambda f: f.annotation

        ref_map = {}

        plan_fields: list[InitPlan.Field] = []
        for i, f in enumerate(ctx.cs.fields):
            plan_fields.append(self._plan_field(
                ctx,
                i,
                f,
                get_field_ann(f),
                ref_map,
            ))

        mro_v_ids = set(map(id, ctx[MroDict].values()))
        props_by_fget_id = {
            id(v.fget): v
            for v in ctx[MroDict].values()
            if isinstance(v, property)
            and v.fget is not None
        }
        ifns: list[OpRef[InitFn]] = []
        for i, ifn in enumerate(ctx.cs.init_fns or []):
            if (obj_id := id(ifn)) not in mro_v_ids and obj_id in props_by_fget_id:
                ifn = props_by_fget_id[obj_id].__get__
            elif isinstance(ifn, property):
                ifn = ifn.__get__
            ir: OpRef = OpRef(f'init.init_fns.{i}')
            ref_map[ir] = ifn
            ifns.append(ir)

        vfs: list[InitPlan.ValidateFnWithParams] = []
        for i, vfn in enumerate(ctx.cs.validate_fns or []):
            vfr: OpRef = OpRef(f'init.validate_fns.{i}')
            ref_map[vfr] = vfn.fn
            vfs.append(InitPlan.ValidateFnWithParams(
                fn=vfr,
                params=tuple(vfn.params),
            ))

        post_init_params: tuple[str, ...] | None = None
        if hasattr(ctx.cls, STD_POST_INIT_NAME):
            post_init_params = tuple(f.name for f in init_fields.all if f.field_type is FieldType.INIT_VAR)

        return PlanResult(
            InitPlan(
                fields=tuple(plan_fields),

                self_param=SELF_IDENT if 'self' in ctx.cs.fields_by_name else 'self',
                std_params=tuple(f.name for f in init_fields.std),
                kw_only_params=tuple(f.name for f in init_fields.kw_only),

                frozen=ctx.cs.frozen,

                post_init_params=post_init_params,

                init_fns=tuple(ifns),

                validate_fns=tuple(vfs),
            ),
            ref_map,
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

        proto_lines = [
            f'def __init__(',
            f'    {bs.self_param},',
            *[
                f'    {p},'
                for p in params
            ],
            f') -> {NONE_IDENT}:',
        ]

        # body

        lines = []

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
                f'            obj={bs.self_param},',
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
                f'            obj={bs.self_param},',
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
                f'            obj={bs.self_param},',
                f'            fn={vfn.fn.ident()},',
                f'        )',
            ])

        # setattr

        sab = SetattrSrcBuilder(
            object_ident=bs.self_param,
        )
        for f in bs.fields:
            if f.field_type != FieldType.INSTANCE:
                continue
            lines.extend([
                f'    {l}'
                for l in sab(f.name, f.name, frozen=bs.frozen, override=f.override)
            ])

        # post-init

        if (pia := bs.post_init_params) is not None:
            lines.append(
                f'    {bs.self_param}.{STD_POST_INIT_NAME}({", ".join(pia)})',
            )

        for ifn in bs.init_fns:
            ors.add(ifn)
            lines.append(
                f'    {ifn.ident()}({bs.self_param})',
            )

        #

        if not lines:
            lines.append(
                '    pass',
            )

        return [
            AddMethodOp('__init__', '\n'.join([*proto_lines, *lines]), frozenset(ors)),
        ]
