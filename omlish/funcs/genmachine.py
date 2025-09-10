"""
TODO:
 - feed_iter helper
 - accept yielding outputs on transitions, *except* on initial state - add test

See:
 - https://github.com/pytransitions/transitions
"""
import typing as ta


I = ta.TypeVar('I')
O = ta.TypeVar('O')

# MachineGen: ta.TypeAlias = ta.Generator[ta.Iterable[O] | None, I | None, ta.Optional[MachineGen[I, O]]]
MachineGen: ta.TypeAlias = ta.Generator[ta.Any, ta.Any, ta.Any]


##


class GenMachine(ta.Generic[I, O]):
    """
    Generator-powered state machine. Generators are sent an `I` object and yield any number of `O` objects in response,
    until they yield a `None` by accepting new input. Generators may return a new generator to switch states, or return
    `None` to terminate.
    """

    def __init__(self, initial: MachineGen | None = None) -> None:
        super().__init__()

        if initial is None:
            initial = self._initial_state()
            if initial is None:
                raise TypeError('No initial state')

        self._gen = initial

        if (n := next(self._gen)) is not None:  # noqa
            raise GenMachine.NotStartedError

    def _initial_state(self) -> MachineGen | None:
        return None

    _gen: MachineGen | None

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}<{self.state}>'

    #

    @property
    def state(self) -> str | None:
        if self._gen is not None:
            return self._gen.gi_code.co_qualname  # type: ignore[attr-defined]
        return None

    #

    @property
    def closed(self) -> bool:
        return self._gen is None

    def close(self) -> None:
        if self._gen is not None:
            self._gen.close()
            self._gen = None

    def __enter__(self) -> ta.Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    #

    class Error(Exception):
        pass

    class NotStartedError(Error):
        pass

    class ClosedError(Error):
        pass

    class StateError(Error):
        pass

    #

    def __call__(self, i: I) -> ta.Iterator[O]:
        if self._gen is None:
            raise GenMachine.ClosedError

        gi: I | None = i
        while True:
            try:
                while (o := self._gen.send(gi)) is not None:
                    gi = None
                    yield from o

                break

            except StopIteration as s:
                if (sv := s.value) is None:
                    self._gen = None
                    return None

                self._gen = sv
                gi = None
