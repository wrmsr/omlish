import typing as ta

from ... import dataclasses as dc
from ..types import Tag


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class Id:
    """A utility dataclass intended to be used as a key tag for disambiguation."""

    v: int

    tag: ta.Any = dc.xfield(
        default=None,
        kw_only=True,
        validate=lambda o: not isinstance(o, Tag),
        repr_fn=dc.opt_repr,
    )
