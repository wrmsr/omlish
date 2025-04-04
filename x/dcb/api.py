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
from omlish import lang
from omlish import reflect as rfl

from .processing import ClassProcessor
from .specs import CLASS_SPEC_ATTR
from .specs import ClassSpec
from .specs import FieldSpec
from .types import DefaultFactory
from .types import InitFn
from .types import ReprFn


##


METADATA_ATTR = '__dataclass_metadata__'


def _append_cls_md(k, v):
    lang.get_caller_cls_dct(1).setdefault(METADATA_ATTR, {}).setdefault(k, []).append(v)


#


class _InitMetadata(lang.Marker):
    pass


def init(obj):
    _append_cls_md(_InitMetadata, obj)
    return obj


##


class _NoDefault(lang.Marker):
    pass


@dc.dataclass(frozen=True)
class Field:
    default: ta.Any = _NoDefault
    default_factory: ta.Callable[..., ta.Any] | None = None

    repr_fn: ReprFn | None = None
    repr_priority: int | None = None
    override: bool = False


def field(
        *,
        default: ta.Any = _NoDefault,
        default_factory: ta.Callable[..., ta.Any] | None = None,

        repr_fn: ReprFn | None = None,
        repr_priority: int | None = None,
        override: bool = False,
) -> ta.Any:
    return Field(
        default=default,
        default_factory=default_factory,

        repr_fn=repr_fn,
        repr_priority=repr_priority,
        override=override,
    )


def dataclass(
        *,
        init=True,  # noqa
        repr=True,  # noqa
        eq=True,
        order=False,
        unsafe_hash=False,
        frozen=False,

        match_args=True,

        cache_hash: bool = False,
        override: bool = False,
):
    def inner(cls):
        fsl: list[FieldSpec] = []

        anns = rfl.get_annotations(cls)
        for att, ann in anns.items():
            try:
                fv = cls.__dict__[att]
            except KeyError:
                fld = Field()
            else:
                if isinstance(fv, Field):
                    fld = fv
                else:
                    fld = Field(default=fv)

            dfl: lang.Maybe[ta.Any] = lang.empty()
            if fld.default is not _NoDefault:
                check.state(fld.default_factory is None)
                dfl = lang.just(fld.default)
            elif fld.default_factory is not None:
                dfl = lang.just(DefaultFactory(fld.default_factory))

            fsl.append(FieldSpec(
                name=att,
                annotation=ann,

                default=dfl,

                repr_fn=fld.repr_fn,
                repr_priority=fld.repr_priority,
                override=fld.override,
            ))

        init_fns: list[InitFn] = []
        if (cls_md_dct := cls.__dict__.get(METADATA_ATTR)):
            if (md_ifs := cls_md_dct.get(_InitMetadata)):
                for md_if in md_ifs:
                    init_fns.append(md_if)

        cs = ClassSpec(
                fields=fsl,

                init=init,
                repr=repr,
                eq=eq,
                order=order,
                unsafe_hash=unsafe_hash,
                frozen=frozen,

                match_args=match_args,

                cache_hash=cache_hash,
                override=override,

                init_fns=init_fns,
        )

        setattr(cls, CLASS_SPEC_ATTR, cs)

        ClassProcessor(cls, cs).process()

        return cls

    return inner


