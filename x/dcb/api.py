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

from omlish import reflect as rfl

from .processing import ClassProcessor
from .specs import CLASS_SPEC_ATTR
from .specs import ClassSpec
from .specs import FieldSpec


##


@dc.dataclass(frozen=True)
class Field:
    pass


def field() -> Field:
    return Field()


def dataclass(
        *,
        frozen: bool = False,
        repr: bool = True,  # noqa
):
    def inner(cls):
        fsl: list[FieldSpec] = []

        anns = rfl.get_annotations(cls)
        for att, ann in anns.items():
            fsl.append(FieldSpec(
                name=att,
                annotation=ann,
            ))

        cs = ClassSpec(
                fields=fsl,

                frozen=frozen,
                repr=repr,
        )

        setattr(cls, CLASS_SPEC_ATTR, cs)

        ClassProcessor(cls, cs).process()

        return cls

    return inner


