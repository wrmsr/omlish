# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import typing as ta

from omlish.lite.check import check_isinstance
from omlish.lite.strings import snake_case


CommandT = ta.TypeVar('CommandT', bound='Command')
CommandOutputT = ta.TypeVar('CommandOutputT', bound='Command.Output')


##


@dc.dataclass(frozen=True)
class Command(abc.ABC, ta.Generic[CommandOutputT]):
    @dc.dataclass(frozen=True)
    class Output(abc.ABC):  # noqa
        pass

    @ta.final
    def execute(self, executor: 'CommandExecutor') -> CommandOutputT:
        return check_isinstance(executor.execute(self), self.Output)


##


class CommandExecutor(abc.ABC, ta.Generic[CommandT, CommandOutputT]):
    @abc.abstractmethod
    def execute(self, i: CommandT) -> CommandOutputT:
        raise NotImplementedError


##


CommandNameMap = ta.NewType('CommandNameMap', ta.Mapping[str, ta.Type[Command]])


def build_command_name_map(cmds: ta.Iterable[ta.Type[Command]]) -> CommandNameMap:
    dct = {}
    for cmd in cmds:
        if not (cls_name := cmd.__name__).endswith('Command'):
            raise NameError(cls_name)

        name = snake_case(cls_name[:-len('Command')])
        if name in dct:
            raise

        dct[name] = cmd

    return CommandNameMap(dct)
