"""
TODO:
 - collect init_fn's / validate_fns from superclass ClassSpecs
"""
import inspect
import typing as ta

from .... import check
from .... import lang
from ...internals import STD_FIELDS_ATTR
from ...internals import STD_PARAMS_ATTR
from ...processing.driving import drive_cls_processing
from ...specs import ClassSpec
from ...utils import class_decorator
from ..fields.building import build_cls_std_fields
from ..fields.conversion import std_field_to_field_spec
from .metadata import extract_cls_metadata
from .params import build_spec_std_params


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

        #

        metadata: ta.Sequence[ta.Any] | None = None,

        reorder: bool | None = None,
        cache_hash: bool | None = None,
        generic_init: bool | None = None,
        override: bool | None = None,
        repr_id: bool | None = None,

        #

        _plan_only: bool = False,
):
    if isinstance(metadata, ta.Mapping):
        raise TypeError(metadata)

    #

    cls = check.not_none(cls)

    #

    fields = build_cls_std_fields(
        cls,
        kw_only=kw_only,
    )
    setattr(cls, STD_FIELDS_ATTR, fields)

    #

    fsl = [
        std_field_to_field_spec(
            f,
            set_metadata=True,
        )
        for f in fields.values()
    ]

    #

    cmd = extract_cls_metadata(cls, deep=True)

    vfp_lst: list[ClassSpec.ValidateFnWithParams] = []
    for md_vf in cmd.validate_fns or []:
        if isinstance(md_vf, staticmethod):
            md_vf = md_vf.__func__
        vfp_lst.append(ClassSpec.ValidateFnWithParams(
            md_vf,
            [p.name for p in inspect.signature(md_vf).parameters.values()],
        ))

    #

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

        #

        metadata=(
            *(cmd.user_metadata or []),
            *(metadata or []),
        ) or None,

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

        init_fns=cmd.init_fns or None,
        validate_fns=vfp_lst or None,
    )

    #

    std_params = build_spec_std_params(cs)
    check.not_in(STD_PARAMS_ATTR, cls.__dict__)
    setattr(cls, STD_PARAMS_ATTR, std_params)

    #

    return drive_cls_processing(
        cls,
        cs,
        plan_only=_plan_only,
    )
