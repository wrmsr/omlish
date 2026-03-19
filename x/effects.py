"""
https://thenewstack.io/did-signals-just-land-in-react/
https://pomb.us/build-your-own-react/
https://plainvanillaweb.com/blog/articles/2024-08-30-poor-mans-signals/
"""
from __future__ import annotations

import contextlib
import dataclasses as dc
import threading
import typing as ta

from omlish import cached
from omlish import check
from omlish import lang
from omlish import reflect as rfl


T = ta.TypeVar('T')


##


class Ref(lang.Final, ta.Generic[T]):
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

    #

    _access_listeners_tl: ta.ClassVar[threading.local] = threading.local()
    _access_listeners_tl.lst = []

    @classmethod
    def _current_access_listeners(cls) -> ta.Sequence[ta.Callable[[Ref], None]]:
        return cls._access_listeners_tl.lst

    @classmethod
    @contextlib.contextmanager
    def push_access_listener(cls, fn: ta.Callable[[Ref], None]) -> ta.Iterator[None]:
        cls._access_listeners_tl.lst.append(fn)
        try:
            yield
        finally:
            if cls._access_listeners_tl.lst.pop() is not fn:
                raise RuntimeError

    #

    _v: T

    @cached.property
    def _value_type(self) -> ta.Any:
        return check.single(ta.get_args(rfl.get_orig_class(self)))

    def add_listener(self, *ls: ta.Callable[[Ref[T]], None]) -> ta.Self:
        self._listeners.extend(ls)
        return self

    def get(self) -> T:
        for fn in self._current_access_listeners():
            fn(self)
        return self._v

    def __call__(self) -> T:
        return self.get()

    def __bool__(self) -> ta.NoReturn:
        raise TypeError

    def set(self, v: T) -> None:
        self._v = v
        for l in self._listeners:
            l(self)


##


class Effects:
    @dc.dataclass(eq=False)
    class _Effect(ta.Generic[T]):
        fn: ta.Callable[[], T]
        inputs: ta.MutableSet[Ref] = dc.field(default_factory=set)
        output: Ref[T] | None = None

    def __init__(self) -> None:
        super().__init__()

        self._effects_by_fn: dict[ta.Callable[[], None], Effects._Effect] = {}
        self._effects_by_output: dict[Ref, Effects._Effect] = {}
        self._effect_sets_by_input: dict[Ref, set[Effects._Effect]] = {}
        self._inputs: set[Ref] = set()

    def make_effect(self, fn: ta.Callable[[], None]) -> Ref[T]:
        if fn in self._effects_by_fn:
            raise KeyError(fn)

        e = Effects._Effect(fn)
        self._effects_by_fn[fn] = e

        self._run_effect(e)
        return check.not_none(e.output)

    def _run_effect(self, e: _Effect) -> None:
        with Ref.push_access_listener(e.inputs.add):
            v = e.fn()

        for r in e.inputs:
            self._effect_sets_by_input.setdefault(r, set()).add(e)
            if r not in self._inputs:
                r.add_listener(self._on_ref_update)
                self._inputs.add(r)

        if (out := e.output) is None:
            out = e.output = Ref(v)
            self._effects_by_output[out] = e
        else:
            out.set(v)

    def _on_ref_update(self, ref: Ref) -> None:
        for e in self._effect_sets_by_input[ref]:
            self._run_effect(e)


##


EFFECTS = Effects()

make_effect = EFFECTS.make_effect


def _main() -> None:
    x = Ref[int](0)
    y = Ref[int](0)

    @make_effect
    def x_plus_y() -> str:
        return f'{x()=} + {y()=} = {(x() + y())=}'

    @make_effect
    def print_x_plus_y() -> None:
        print(f'{x_plus_y()=}')

    x.set(1)
    y.set(2)


if __name__ == '__main__':
    _main()
