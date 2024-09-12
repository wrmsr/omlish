"""
See:
 - https://github.com/pytransitions/transitions
"""
import typing as ta


I = ta.TypeVar('I')
O = ta.TypeVar('O')

# MachineGen: ta.TypeAlias = ta.Generator[ta.Iterable[O] | None, I, ta.Optional[MachineGen[I, O]]]
MachineGen: ta.TypeAlias = ta.Generator[ta.Any, ta.Any, ta.Any]


##


class IllegalStateError(Exception):
    pass


class GenMachine(ta.Generic[I, O]):
    """
    Generator-powered state machine. Generators are sent an `I` object and yield any number of `O` objects in response,
    until they yield a `None` by accepting new input. Generators may return a new generator to switch states, or return
    `None` to terminate.
    """

    def __init__(self, initial: MachineGen) -> None:
        super().__init__()
        self._advance(initial)

    @property
    def state(self) -> str | None:
        if self._gen is not None:
            return self._gen.gi_code.co_qualname
        return None

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{hex(id(self))[2:]}<{self.state}>'

    _gen: MachineGen | None

    def _advance(self, gen: MachineGen) -> None:
        self._gen = gen
        if (n := next(self._gen)) is not None:  # noqa
            raise IllegalStateError

    def __call__(self, i: I) -> ta.Iterable[O]:
        if self._gen is None:
            raise IllegalStateError
        try:
            while (o := self._gen.send(i)) is not None:
                yield from o
        except StopIteration as s:
            if s.value is None:
                self._gen = None
                return None
            self._advance(s.value)
