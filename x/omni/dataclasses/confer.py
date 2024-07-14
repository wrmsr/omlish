import dataclasses as dc
import typing as ta

from .. import check
from .internals import DataclassParams
from .reflect import get_cls_spec
from .types import Conferrer
from .types import EXTRA_PARAMS_CONFER_DEFAULTS
from .types import ExtraParams
from .types import METACLASS_PARAMS_CONFER_DEFAULTS
from .types import MetaclassParams
from .types import PARAMS_CONFER_DEFAULTS


def _build_ctx(
    params: DataclassParams,
    extra_params: ExtraParams,
    metaclass_params: ta.Optional[MetaclassParams] = None,
) -> ta.Mapping[str, ta.Any]:
    ctx = {
        **{a: getattr(params, a) for a in DataclassParams.__slots__},
        **{fld.name: getattr(extra_params, fld.name) for fld in dc.fields(ExtraParams)},
    }
    if metaclass_params is not None:
        ctx.update({fld.name: getattr(metaclass_params, fld.name) for fld in dc.fields(MetaclassParams)})
    return ctx


def confer_params(
        bases: ta.Sequence[type],
        params: DataclassParams,
        extra_params: ExtraParams,
        metaclass_params: ta.Optional[MetaclassParams] = None,
) -> ta.Tuple[
    DataclassParams,
    ExtraParams,
    ta.Optional[MetaclassParams],
]:
    check.isinstance(params, DataclassParams)
    check.isinstance(extra_params, ExtraParams)
    if metaclass_params is not None:
        check.isinstance(metaclass_params, MetaclassParams)

    sub = _build_ctx(params, extra_params, metaclass_params)

    params_confers = {}
    extra_params_confers = {}
    metaclass_params_confers = {}

    for base in bases:
        if not dc.is_dataclass(base):
            continue
        base_spec = get_cls_spec(base)
        confer = base_spec.extra_params.confer
        if not confer:
            continue

        sup = _build_ctx(base_spec.params, base_spec.extra_params, base_spec.metaclass_params)

        def update(given_params, base_params, confer_defaults, conferred):
            for att, val in confer_defaults.items():
                if getattr(given_params, att) is not dc.MISSING or att not in confer:
                    continue
                weak = False
                if isinstance(confer, ta.Mapping):
                    if isinstance(confer[att], Conferrer):
                        val = confer[att].fn(att, sub, sup, bases)
                        weak = confer[att].weak
                    else:
                        val = confer[att]
                elif base_params is not None:
                    val = getattr(base_params, att)
                if val is dc.MISSING:
                    continue
                if att in conferred:
                    if conferred[att] != val and not weak:
                        raise ValueError(f'Incompatible conferred params: base={base} a={att}')
                else:
                    conferred[att] = val

        update(params, base_spec.params, PARAMS_CONFER_DEFAULTS, params_confers)
        update(extra_params, base_spec.extra_params, EXTRA_PARAMS_CONFER_DEFAULTS, extra_params_confers)
        if metaclass_params is not None:
            update(metaclass_params, base_spec.metaclass_params, METACLASS_PARAMS_CONFER_DEFAULTS, metaclass_params_confers)  # noqa

    params_dict = {
        **PARAMS_CONFER_DEFAULTS,
        **{
            a: v for a in DataclassParams.__slots__
            for v in [getattr(params, a)]
            if a not in PARAMS_CONFER_DEFAULTS or v is not dc.MISSING
        },
        **params_confers,
    }
    check.not_in(dc.MISSING, params_dict.values())
    params = DataclassParams(**params_dict)

    extra_params_dict = {
        **EXTRA_PARAMS_CONFER_DEFAULTS,
        **{
            a: v
            for fld in dc.fields(ExtraParams)
            for a in [fld.name]
            for v in [getattr(extra_params, a)]
            if a not in EXTRA_PARAMS_CONFER_DEFAULTS or v is not dc.MISSING
        },
        **extra_params_confers,
    }
    check.not_in(dc.MISSING, extra_params_dict.values())
    extra_params = ExtraParams(**extra_params_dict)

    if metaclass_params is not None:
        metaclass_params_dict = {
            **METACLASS_PARAMS_CONFER_DEFAULTS,
            **{
                a: v
                for fld in dc.fields(MetaclassParams)
                for a in [fld.name]
                for v in [getattr(metaclass_params, a)]
                if a not in METACLASS_PARAMS_CONFER_DEFAULTS or v is not dc.MISSING
            },
            **metaclass_params_confers,
        }
        check.not_in(dc.MISSING, metaclass_params_dict.values())
        metaclass_params = MetaclassParams(**metaclass_params_dict)

    return params, extra_params, metaclass_params
