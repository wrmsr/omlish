"""
https://thenewstack.io/did-signals-just-land-in-react/
https://pomb.us/build-your-own-react/
"""
from __future__ import annotations

import typing as ta

from omlish import cached
from omlish import check
from omlish import reflect as rfl


T = ta.TypeVar('T')


class Ref(ta.Generic[T]):
    def __init__(
            self,
            initial: T,
            name: str | None = None,
            *,
            listeners: list[ta.Callable[[Ref[T]], None]] | None = None,
    ) -> None:
        super().__init__()
        self._name = name
        self._listeners: list[ta.Callable[[Ref[T]], None]] = list(listeners) if listeners is not None else []
        self.set(initial)

    _v: T

    @cached.property
    def _value_type(self) -> ta.Any:
        return check.single(ta.get_args(rfl.get_orig_class(self)))

    def add_listener(self, *ls: ta.Callable[[Ref[T]], None]) -> ta.Self:
        self._listeners.extend(ls)
        return self

    def get(self) -> T:
        return self._v

    def set(self, v: T) -> None:
        self._v = v
        for l in self._listeners:
            l(self)


def _main() -> None:
    print(Ref[int](0)._value_type)


if __name__ == '__main__':
    _main()
