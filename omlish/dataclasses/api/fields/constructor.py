import collections
import dataclasses as dc
import typing as ta

from ...specs import CoerceFn
from ...specs import ReprFn
from ...specs import ValidateFn
from .metadata import extra_field_params


##


def field(
        default=dc.MISSING,
        *,
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
