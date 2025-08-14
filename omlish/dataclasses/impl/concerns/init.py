"""
TODO:
 - ensure all 'init' fields work - non-instance
 - special case 'None' default, most common
"""
import dataclasses as dc
import itertools
import typing as ta

from .... import check
from ..._internals import STD_POST_INIT_NAME
from ...inspect import FieldsInspection
from ...specs import CoerceFn
from ...specs import DefaultFactory
from ...specs import FieldSpec
from ...specs import FieldType
from ...specs import InitFn
from ...specs import ValidateFn
from ..generation.base import Generator
from ..generation.base import Plan
from ..generation.base import PlanResult
from ..generation.globals import FIELD_FN_VALIDATION_ERROR_GLOBAL
from ..generation.globals import FIELD_TYPE_VALIDATION_ERROR_GLOBAL
from ..generation.globals import FN_VALIDATION_ERROR_GLOBAL
from ..generation.globals import HAS_DEFAULT_FACTORY_GLOBAL
from ..generation.globals import ISINSTANCE_GLOBAL
from ..generation.globals import NONE_GLOBAL
from ..generation.idents import SELF_IDENT
from ..generation.ops import AddMethodOp
from ..generation.ops import Op
from ..generation.ops import OpRef
from ..generation.ops import Ref
from ..generation.registry import register_generator_type
from ..generation.utils import SetattrSrcBuilder
from ..processing.base import ProcessingContext
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

        init: bool

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

    slots: bool

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

        check_type_ref: OpRef[type | tuple[type, ...]] | None = None
        if f.check_type is not None and f.check_type is not False:
            check_type_arg: ta.Any
            if isinstance(f.check_type, tuple):
                check_type_arg = tuple(type(None) if e is None else check.isinstance(e, type) for e in f.check_type)
            elif isinstance(f.check_type, type):
                check_type_arg = f.check_type
            elif f.check_type is True:
                check_type_arg = f.annotation
            else:
                raise TypeError(f.check_type)
            check_type_ref = OpRef(f'init.fields.{i}.check_type')
            ref_map[check_type_ref] = check_type_arg

        return InitPlan.Field(
            name=f.name,
            annotation=ann_ref,

            default=default_ref,
            default_factory=default_factory_ref,

            init=f.init,

            override=f.override or ctx.cs.override,

            field_type=f.field_type,

            coerce=coerce,
            validate=validate_ref,

            check_type=check_type_ref,
        )

    def plan(self, ctx: ProcessingContext) -> PlanResult[InitPlan] | None:
        if '__init__' in ctx.cls.__dict__ or not ctx.cs.init:
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

        ref_map: dict = {}

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
        init_fns: list[OpRef[InitFn]] = []
        for i, init_fn in enumerate(ctx.cs.init_fns or []):
            if (obj_id := id(init_fn)) not in mro_v_ids and obj_id in props_by_fget_id:
                init_fn = props_by_fget_id[obj_id].__get__
            elif isinstance(init_fn, property):
                init_fn = init_fn.__get__
            init_fn_ref: OpRef = OpRef(f'init.init_fns.{i}')
            ref_map[init_fn_ref] = init_fn
            init_fns.append(init_fn_ref)

        validate_fns: list[InitPlan.ValidateFnWithParams] = []
        for i, validate_fn in enumerate(ctx.cs.validate_fns or []):
            validate_fn_ref: OpRef = OpRef(f'init.validate_fns.{i}')
            ref_map[validate_fn_ref] = validate_fn.fn
            validate_fns.append(InitPlan.ValidateFnWithParams(
                fn=validate_fn_ref,
                params=tuple(validate_fn.params),
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

                slots=ctx.cs.slots,

                post_init_params=post_init_params,

                init_fns=tuple(init_fns),

                validate_fns=tuple(validate_fns),
            ),
            ref_map,
        )

    def generate(self, plan: InitPlan) -> ta.Iterable[Op]:
        refs: set[Ref] = set()

        fields_by_name = {f.name: f for f in plan.fields}

        # proto

        params: list[str] = []
        seen_kw_only = False
        for fn, kw_only in itertools.chain(
            [(fn, False) for fn in plan.std_params],
            [(fn, True) for fn in plan.kw_only_params],
        ):
            f = fields_by_name[fn]
            if kw_only:
                if not seen_kw_only:
                    params.append('*')
                    seen_kw_only = True
            elif seen_kw_only:
                raise TypeError(f'non-keyword-only argument {f.name!r} follows keyword-only argument(s)')

            refs.add(f.annotation)
            p = f'{f.name}: {f.annotation.ident()}'

            if f.default_factory is not None:
                check.none(f.default)
                p += f' = {HAS_DEFAULT_FACTORY_GLOBAL.ident}'
                refs.add(HAS_DEFAULT_FACTORY_GLOBAL)
            elif f.default is not None:
                check.none(f.default_factory)
                refs.add(f.default)
                p += f' = {f.default.ident()}'

            params.append(p)

        proto_lines = [
            f'def __init__(',
            f'    {plan.self_param},',
            *[
                f'    {p},'
                for p in params
            ],
            f') -> {NONE_GLOBAL.ident}:',
        ]
        refs.add(NONE_GLOBAL)

        # body

        lines = []

        # defaults

        values: dict[str, str] = {
            plan.self_param: plan.self_param,
        }

        for f in plan.fields:
            if f.default_factory is not None:
                check.none(f.default)
                refs.add(f.default_factory)
                if f.init:
                    lines.extend([
                        f'    if {f.name} is {HAS_DEFAULT_FACTORY_GLOBAL.ident}:',
                        f'        {f.name} = {f.default_factory.ident()}()',
                    ])
                    refs.add(HAS_DEFAULT_FACTORY_GLOBAL)
                else:
                    lines.append(
                        f'    {f.name} = {f.default_factory.ident()}()',
                    )
                values[f.name] = f.name

            elif f.init:
                if f.default is not None:
                    check.none(f.default_factory)
                    values[f.name] = f.name

                else:
                    values[f.name] = f.name

            elif plan.slots and f.default is not None:
                refs.add(f.default)
                lines.append(
                    f'    {f.name} = {f.default.ident()}',
                )
                values[f.name] = f.name

        # coercion

        for f in plan.fields:
            if isinstance(f.coerce, bool) and f.coerce:
                lines.append(
                    f'    {f.name} = {f.annotation.ident()}({values[f.name]})',
                )
                values[f.name] = f.name
            elif isinstance(f.coerce, OpRef):
                refs.add(f.coerce)
                lines.append(
                    f'    {f.name} = {f.coerce.ident()}({values[f.name]})',
                )
                values[f.name] = f.name

        # field validation

        for f in plan.fields:
            if f.check_type is None:
                continue
            refs.add(f.check_type)
            lines.extend([
                f'    if not {ISINSTANCE_GLOBAL.ident}({values[f.name]}, {f.check_type.ident()}): ',
                f'        raise {FIELD_TYPE_VALIDATION_ERROR_GLOBAL.ident}(',
                f'            obj={plan.self_param},',
                f'            type={f.check_type.ident()},',
                f'            field={f.name!r},',
                f'            value={values[f.name]},',
                f'        )',
            ])
            refs.add(ISINSTANCE_GLOBAL)
            refs.add(FIELD_TYPE_VALIDATION_ERROR_GLOBAL)

        for f in plan.fields:
            if f.validate is None:
                continue
            refs.add(f.validate)
            lines.extend([
                f'    if not {f.validate.ident()}({values[f.name]}): ',
                f'        raise {FIELD_FN_VALIDATION_ERROR_GLOBAL.ident}(',
                f'            obj={plan.self_param},',
                f'            fn={f.validate.ident()},',
                f'            field={f.name!r},',
                f'            value={values[f.name]},',
                f'        )',
            ])
            refs.add(FIELD_FN_VALIDATION_ERROR_GLOBAL)

        # setattr

        sab = SetattrSrcBuilder(
            object_ident=plan.self_param,
        )
        for f in plan.fields:
            if f.name not in values or f.field_type != FieldType.INSTANCE:
                continue
            lines.extend([
                f'    {l}'
                for l in sab(
                    f.name,
                    values[f.name],
                    frozen=plan.frozen,
                    override=f.override,
                )
            ])
        refs.update(sab.refs)

        # fn validation

        for vfn in plan.validate_fns or []:
            refs.add(vfn.fn)
            if vfn.params:
                lines.extend([
                    f'    if not {vfn.fn.ident()}(',
                    *[
                        f'        {values[p]},'
                        for p in vfn.params
                    ],
                    f'    ):',
                ])
            else:
                lines.append(
                    f'    if not {vfn.fn.ident()}():',
                )
            lines.extend([
                f'        raise {FN_VALIDATION_ERROR_GLOBAL.ident}(',
                f'            obj={plan.self_param},',
                f'            fn={vfn.fn.ident()},',
                f'        )',
            ])
            refs.add(FN_VALIDATION_ERROR_GLOBAL)

        # post-init

        if (pia := plan.post_init_params) is not None:
            if pia:
                lines.extend([
                    f'    {plan.self_param}.{STD_POST_INIT_NAME}(',
                    *[
                        f'        {values[p]},'
                        for p in pia
                    ],
                    f'    )',
                ])
            else:
                lines.append(
                    f'    {plan.self_param}.{STD_POST_INIT_NAME}()',
                )

        for init_fn in plan.init_fns:
            refs.add(init_fn)
            lines.append(
                f'    {init_fn.ident()}({plan.self_param})',
            )

        #

        if not lines:
            lines.append(
                '    pass',
            )

        return [
            AddMethodOp(
                '__init__',
                '\n'.join([*proto_lines, *lines]),
                frozenset(refs),
            ),
        ]
