# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import typing as ta


CommandT = ta.TypeVar('CommandT', bound='Command')
CommandOutputT = ta.TypeVar('CommandOutputT', bound='Command.Output')


##


@dc.dataclass(frozen=True)
class Command(abc.ABC, ta.Generic[CommandOutputT]):
    @dc.dataclass(frozen=True)
    class Output(abc.ABC):  # noqa
        pass


##


class CommandExecutor(abc.ABC, ta.Generic[CommandT, CommandOutputT]):
    @abc.abstractmethod
    def execute(self, i: CommandT) -> CommandOutputT:
        raise NotImplementedError
