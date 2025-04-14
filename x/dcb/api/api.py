"""
TODO:
 - strip metadata out of __dict__ after construction
"""
import collections
import dataclasses as dc
import inspect
import typing as ta

from omlish import check
from omlish import lang

from ..utils import class_decorator
from ..processing.driving import drive_cls_processing
from ..specs import ClassSpec
from ..specs import CoerceFn
from ..specs import DefaultFactory
from ..specs import FieldSpec
from ..specs import ReprFn
from ..specs import ValidateFn
from ..std.conversion import class_spec_to_std_params
from ..internals import STD_PARAMS_ATTR
from ..std.conversion import std_field_to_field_spec
from .fields import build_cls_std_fields
from ..std.conversion import std_field_to_spec_field_default
from .fields import install_built_cls_std_fields
from .metadata import extract_cls_metadata
from .fields import extra_field_params


##


def field(
        *,
        default=dc.MISSING,
        default_factory=dc.MISSING,
        init=True,
        repr=True,  # noqa
        hash=None,  # noqa
        compare=True,
        metadata=None,
        kw_only=dc.MISSING,

        coerce: bool | CoerceFn | None = None,
        validate: ValidateFn | None = None,  # noqa
        check_type: bool | type | tuple[type | None, ...] | None = None,
        override: bool = False,
        repr_fn: ReprFn | None = None,
        repr_priority: int | None = None,
) -> ta.Any:
    efp = extra_field_params(
        coerce=coerce,
        validate=validate,
        check_type=check_type,
        override=override,
        repr_fn=repr_fn,
        repr_priority=repr_priority,
    )

    if metadata is None:
        metadata = efp
    else:
        metadata = collections.ChainMap(efp, metadata)  # noqa

    return dc.field(
        default=default,
        default_factory=default_factory,
        init=init,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata=metadata,
        kw_only=kw_only,
    )


##


@class_decorator
def dataclass(
        cls=None,
        *,
        /,

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

        reorder: bool = False,
        cache_hash: bool = False,
        generic_init: bool = False,
        override: bool = False,
        repr_id: bool = False,
):
    cls = check.not_none(cls)

    csf = build_cls_std_fields(cls, kw_only=kw_only)
    install_built_cls_std_fields(cls, csf)

    fsl: list[FieldSpec] = []
    for f in csf.fields.values():
        try:
            fs = f.metadata[FieldSpec]
        except KeyError:
            pass
        else:
            fsl.append(fs)
            continue

        dfl = std_field_to_spec_field_default(f)

        fs = std_field_to_field_spec(f)

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
        kw_only=kw_only,
        slots=slots,
        weakref_slot=weakref_slot,

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

    install_built_cls_std_fields(cls, csf)

    return drive_cls_processing(cls, cs)
