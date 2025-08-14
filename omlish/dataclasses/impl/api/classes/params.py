import typing as ta

from ..... import check
from ...._internals import STD_PARAMS_ATTR
from ...._internals import StdParams
from ....specs import ClassSpec


##


STD_PARAM_DEFAULTS: ta.Mapping[str, ta.Any] = dict(
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
)

STD_PARAM_ATTRS: tuple[str, ...] = tuple(STD_PARAM_DEFAULTS)


##


class SpecDataclassParams(StdParams):
    __slots__ = (*StdParams.__slots__, '_spec')

    def __init__(
            self,
            init,
            repr,  # noqa
            eq,
            order,
            unsafe_hash,
            frozen,
            match_args,
            kw_only,
            slots,
            weakref_slot,
            *args: ta.Any,
            spec: ClassSpec,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(
            init,
            repr,
            eq,
            order,
            unsafe_hash,
            frozen,
            match_args,
            kw_only,
            slots,
            weakref_slot,
            *args,
            **kwargs,
        )

        self._spec = spec

    def __repr__(self) -> str:
        r = super().__repr__()
        return f'{self.__class__.__name__}{r[r.index("("):]}'


def build_spec_std_params(cs: ClassSpec) -> 'SpecDataclassParams':
    return SpecDataclassParams(
        init=cs.init,
        repr=cs.repr,
        eq=cs.eq,
        order=cs.order,
        unsafe_hash=cs.unsafe_hash,
        frozen=cs.frozen,

        match_args=cs.match_args,
        kw_only=cs.kw_only,
        slots=cs.slots,
        weakref_slot=cs.weakref_slot,

        spec=cs,
    )


def get_class_spec(cls: type) -> ClassSpec | None:
    check.isinstance(cls, type)

    sp = getattr(cls, STD_PARAMS_ATTR)
    if not isinstance(sp, SpecDataclassParams):
        return None

    return check.isinstance(sp._spec, ClassSpec)  # noqa
