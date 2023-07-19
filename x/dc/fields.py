import dataclasses as dc

from .params import ExField


MISSING = dc.MISSING


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
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError('cannot specify both default and default_factory')

    ex = ExField(
        default=default,
    )

    return dc.Field(
        default,
        default_factory,
        init,
        repr,
        hash,
        compare,
        metadata,
        kw_only,
    )


