import dataclasses as dc
import typing as ta

from ..specs import ClassSpec
from ..std import STD_PARAMS_ATTR
from ..std import StdParams


##


class SpecStdParams(StdParams):
    __slots__ = (*StdParams.__slots__, 'spec')

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

        self.spec = spec

    def __repr__(self) -> str:
        r = super().__repr__()
        return f'{self.__class__.__name__}{r[r.index("("):]}'


##


@dc.dataclass()
class Foo:
    x: int


def test_std_params():
    ap = getattr(Foo, STD_PARAMS_ATTR)
    cs = ClassSpec(fields=[])  # noqa
    print(ap)
