"""
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
import typing as ta

from omlish import check
from omlish import reflect as rfl

from .processing import ClassProcessor
from .specs import CLASS_SPEC_ATTR
from .specs import ClassSpec
from .specs import FieldSpec
from .types import ReprFn


##


@dc.dataclass(frozen=True)
class Field:
    repr_fn: ReprFn | None = None
    override: bool = False


def field(
        *,
        repr_fn: ReprFn | None = None,
        override: bool = False,
) -> ta.Any:
    return Field(
        repr_fn=repr_fn,
        override=override,
    )


def dataclass(
        *,
        init=True,
        repr=True,  # noqa
        eq=True,
        order=False,
        unsafe_hash=False,
        frozen=False,

        cache_hash: bool = False,
        override: bool = False,
):
    def inner(cls):
        fsl: list[FieldSpec] = []

        anns = rfl.get_annotations(cls)
        for att, ann in anns.items():
            try:
                fld = check.isinstance(cls.__dict__[att], Field)
            except (KeyError, TypeError):
                fld = Field()

            fsl.append(FieldSpec(
                name=att,
                annotation=ann,

                repr_fn=fld.repr_fn,
                override=fld.override,
            ))

        cs = ClassSpec(
                fields=fsl,

                init=init,
                repr=repr,
                eq=eq,
                order=order,
                unsafe_hash=unsafe_hash,
                frozen=frozen,

                cache_hash=cache_hash,
                override=override,
        )

        setattr(cls, CLASS_SPEC_ATTR, cs)

        ClassProcessor(cls, cs).process()

        return cls

    return inner


