# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import typing as ta


CommandInputT = ta.TypeVar('CommandInputT', bound='Command.Input')
CommandOutputT = ta.TypeVar('CommandOutputT', bound='Command.Output')


##


class Command(abc.ABC, ta.Generic[CommandInputT, CommandOutputT]):
    @dc.dataclass(frozen=True)
    class Input(abc.ABC):  # noqa
        pass

    @dc.dataclass(frozen=True)
    class Output(abc.ABC):  # noqa
        pass

    @abc.abstractmethod
    def _execute(self, inp: CommandInputT) -> CommandOutputT:
        raise NotImplementedError
