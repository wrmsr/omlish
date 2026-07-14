import typing as ta

from ... import dataclasses as dc
from ... import lang
from ..impl.origins import HasOriginsImpl


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True, eq=False)
class ConstFn(HasOriginsImpl, lang.Final, ta.Generic[T]):
    """An origin tracking provider function for a constant value. Equivalent to `lambda: v` but transparent."""

    v: T

    def __call__(self) -> T:
        return self.v
