"""
TODO:
 - collect init_fn's / validate_fns from superclass ClassSpecs
"""
import collections
import dataclasses as dc
import inspect
import typing as ta

from omlish import check
from omlish import lang

from ..internals import STD_PARAMS_ATTR
from ..processing.driving import drive_cls_processing
from ..specs import ClassSpec
from ..specs import CoerceFn
from ..specs import FieldSpec
from ..specs import ReprFn
from ..specs import ValidateFn
from ..utils import class_decorator
from .classes.metadata import extract_cls_metadata
from .classes.metadata import remove_cls_metadata
from .classes.params import SpecDataclassParams
from .fields.building import build_cls_std_fields
from .fields.building import build_std_field_metadata_update
from .fields.building import install_built_cls_std_fields
from .fields.conversion import std_field_to_field_spec
from .fields.metadata import extra_field_params


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
        override: bool | None = None,
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

    md: ta.Any = metadata
    if md is None:
        md = efp
    else:
        md = collections.ChainMap(efp, md)  # type: ignore[arg-type]

    return dc.field(
        default=default,
        default_factory=default_factory,
        init=init,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata=md,
        kw_only=kw_only,
    )


##


@class_decorator
def dataclass(
        cls=None,
        /,
        *,

        init=True,
        repr=True,  # noqa
        eq=True,
        order=False,
        unsafe_hash=False,
        frozen=False,

        match_args=True,
        kw_only=False,
        slots=False,
        weakref_slot=False,

        reorder: bool | None = None,
        cache_hash: bool | None = None,
        generic_init: bool | None = None,
        override: bool | None = None,
        repr_id: bool | None = None,
):
    cls = check.not_none(cls)

    #

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

        fs = std_field_to_field_spec(f)

        fsl.append(fs)

        build_std_field_metadata_update(f, {FieldSpec: fs}).apply()

    #

    cmd = extract_cls_metadata(cls)
    remove_cls_metadata(cls)

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

        **{
            **(cmd.extra_params or {}),
            **lang.opt_kw(
                reorder=reorder,
                cache_hash=cache_hash,
                generic_init=generic_init,
                override=override,
                repr_id=repr_id,
            ),
        },

        init_fns=cmd.init_fns,
        validate_fns=validate_fns,
    )

    std_params = SpecDataclassParams.from_spec(cs)
    check.not_in(STD_PARAMS_ATTR, cls.__dict__)
    setattr(cls, STD_PARAMS_ATTR, std_params)

    #

    return drive_cls_processing(cls, cs)


def make_dataclass(*args, **kwargs):
    raise NotImplementedError
