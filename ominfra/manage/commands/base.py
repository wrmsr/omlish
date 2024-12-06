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


@dc.dataclass(frozen=True)
class CommandRegistration:
    command_cls: ta.Type[Command]

    name: ta.Optional[str] = None

    @property
    def name_or_default(self) -> str:
        if not (cls_name := self.command_cls.__name__).endswith('Command'):
            raise NameError(cls_name)
        return snake_case(cls_name[:-len('Command')])


CommandRegistrations = ta.NewType('CommandRegistrations', ta.Sequence[CommandRegistration])


##


@dc.dataclass(frozen=True)
class CommandExecutorRegistration:
    command_cls: ta.Type[Command]
    executor_cls: ta.Type[CommandExecutor]


CommandExecutorRegistrations = ta.NewType('CommandExecutorRegistrations', ta.Sequence[CommandExecutorRegistration])


##


CommandNameMap = ta.NewType('CommandNameMap', ta.Mapping[str, ta.Type[Command]])


def build_command_name_map(crs: CommandRegistrations) -> CommandNameMap:
    dct: ta.Dict[str, ta.Type[Command]] = {}
    cr: CommandRegistration
    for cr in crs:
        if (name := cr.name_or_default) in dct:
            raise NameError(name)
        dct[name] = cr.command_cls
    return CommandNameMap(dct)
