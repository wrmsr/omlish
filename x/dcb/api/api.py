"""
TODO:
 - strip metadata out of __dict__ after construction

==

def field(
    *,
    default=MISSING,
    default_factory=MISSING,
    init=True,
    repr=True,
    hash=None,
    compare=True,
    metadata=None,
    kw_only=MISSING,
):

def dataclass(
    cls=None,
    /,
    *,

    init=True,
    repr=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    frozen=False,

    match_args=True,
    kw_only=False,
    slots=False,
    weakref_slot=False,
):
"""
import dataclasses as dc
import inspect
import typing as ta

from omlish import check
from omlish import lang

from ..inspect import get_cls_annotations
from ..processing.driving import drive_cls_processing
from ..specs import ClassSpec
from ..specs import CoerceFn
from ..specs import DefaultFactory
from ..specs import FieldSpec
from ..specs import ReprFn
from ..specs import ValidateFn
from ..std.conversion import class_spec_to_std_params
from ..std.internals import STD_PARAMS_ATTR
from .fields import build_cls_std_fields
from .fields import install_built_cls_std_fields
from .metadata import extract_cls_metadata


##


class _NoDefault(lang.Marker):
    pass


@dc.dataclass(frozen=True)
class Field:
    default: ta.Any = _NoDefault
    default_factory: ta.Callable[..., ta.Any] | None = None

    coerce: bool | CoerceFn | None = None
    validate: ValidateFn | None = None
    check_type: bool | type | tuple[type | None, ...] | None = None
    override: bool = False
    repr_fn: ReprFn | None = None
    repr_priority: int | None = None


def field(
        *,
        default: ta.Any = _NoDefault,
        default_factory: ta.Callable[..., ta.Any] | None = None,

        coerce: bool | CoerceFn | None = None,
        validate: ValidateFn | None = None,  # noqa
        check_type: bool | type | tuple[type | None, ...] | None = None,
        override: bool = False,
        repr_fn: ReprFn | None = None,
        repr_priority: int | None = None,
) -> ta.Any:
    return Field(
        default=default,
        default_factory=default_factory,

        coerce=coerce,
        validate=validate,
        check_type=check_type,
        override=override,
        repr_fn=repr_fn,
        repr_priority=repr_priority,
    )


def dataclass(
        *,
        init=True,  # noqa
        repr=True,  # noqa
        eq=True,
        order=False,
        unsafe_hash=False,
        frozen=False,

        match_args=True,

        reorder: bool = False,
        cache_hash: bool = False,
        generic_init: bool = False,
        override: bool = False,
        repr_id: bool = False,
):
    def inner(cls):
        fsl: list[FieldSpec] = []

        anns = get_cls_annotations(cls)
        for att, ann in anns.items():
            try:
                fv = cls.__dict__[att]
            except KeyError:
                fld = Field()
            else:
                if isinstance(fv, Field):
                    fld = fv
                else:
                    fld = Field(default=fv)

            dfl: lang.Maybe[ta.Any] = lang.empty()
            if fld.default is not _NoDefault:
                check.state(fld.default_factory is None)
                dfl = lang.just(fld.default)
            elif fld.default_factory is not None:
                dfl = lang.just(DefaultFactory(fld.default_factory))

            fsl.append(FieldSpec(
                name=att,
                annotation=ann,

                default=dfl,

                coerce=fld.coerce,
                validate=fld.validate,
                check_type=fld.check_type,
                override=fld.override,
                repr_fn=fld.repr_fn,
                repr_priority=fld.repr_priority,
            ))

        cmd = extract_cls_metadata(cls)
        validate_fns: list[ClassSpec.ValidateFnWithParams] = []
        for md_vf in cmd.validate_fns or []:
            if isinstance(md_vf, staticmethod):
                md_vf = md_vf.__func__
            validate_fns.append(ClassSpec.ValidateFnWithParams(
                md_vf,
                [p.name for p in inspect.signature(md_vf).parameters.values()],
            ))

        cs = ClassSpec(
            fields=fsl,

            init=init,
            repr=repr,
            eq=eq,
            order=order,
            unsafe_hash=unsafe_hash,
            frozen=frozen,

            match_args=match_args,

            reorder=reorder,
            cache_hash=cache_hash,
            generic_init=generic_init,
            override=override,
            repr_id=repr_id,

            init_fns=cmd.init_fns,
            validate_fns=validate_fns,
        )

        std_params = class_spec_to_std_params(cs, use_spec_wrapper=True)
        check.not_in(STD_PARAMS_ATTR, cls.__dict__)
        setattr(cls, STD_PARAMS_ATTR, std_params)

        csf = build_cls_std_fields(cls, kw_only=cs.kw_only)
        install_built_cls_std_fields(cls, csf)

        return drive_cls_processing(cls, cs)

    return inner


