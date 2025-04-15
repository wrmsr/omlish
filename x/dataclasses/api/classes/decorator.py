"""
TODO:
 - collect init_fn's / validate_fns from superclass ClassSpecs
"""
import inspect
import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang

from ...internals import STD_FIELDS_ATTR
from ...internals import STD_PARAMS_ATTR
from ...processing.driving import drive_cls_processing
from ...specs import ClassSpec
from ...specs import FieldSpec
from ...specs import InitFn
from ...utils import class_decorator
from ..fields.building import build_cls_std_fields
from ..fields.building import update_field_metadata
from ..fields.conversion import std_field_to_field_spec
from .metadata import extract_cls_metadata
from .metadata import has_cls_metadata
from .metadata import remove_cls_metadata
from .params import SpecDataclassParams
from .params import get_dataclass_spec


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

    fields = build_cls_std_fields(cls, kw_only=kw_only)
    setattr(cls, STD_FIELDS_ATTR, fields)

    fsl: list[FieldSpec] = []
    for f in fields.values():
        try:
            fs = f.metadata[FieldSpec]
        except KeyError:
            pass
        else:
            fsl.append(fs)
            continue

        fs = std_field_to_field_spec(f)

        fsl.append(fs)

        update_field_metadata(f, {FieldSpec: fs})

    #

    cmd = extract_cls_metadata(cls)
    remove_cls_metadata(cls)

    init_fns: list[InitFn | property] = []
    validate_fns: list[ClassSpec.ValidateFnWithParams] = []

    for bc in cls.__mro__[-1:0:-1]:
        if not dc.is_dataclass(bc):
            check.state(not has_cls_metadata(bc))
            continue
        if (bcs := get_dataclass_spec(bc)) is None:
            continue
        init_fns.extend(bcs.init_fns or [])
        validate_fns.extend(bcs.validate_fns or [])

    init_fns.extend(cmd.init_fns or [])
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

        init_fns=init_fns or None,
        validate_fns=validate_fns or None,
    )

    std_params = SpecDataclassParams.from_spec(cs)
    check.not_in(STD_PARAMS_ATTR, cls.__dict__)
    setattr(cls, STD_PARAMS_ATTR, std_params)

    #

    return drive_cls_processing(cls, cs)
