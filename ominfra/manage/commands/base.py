# ruff: noqa: UP006 UP007 UP045
import abc
import dataclasses as dc
import traceback
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.check import check
from omlish.lite.strings import snake_case
from omlish.logs.protocols import LoggerLike


CommandT = ta.TypeVar('CommandT', bound='Command')
CommandOutputT = ta.TypeVar('CommandOutputT', bound='Command.Output')


##


@dc.dataclass(frozen=True)
class Command(Abstract, ta.Generic[CommandOutputT]):
    @dc.dataclass(frozen=True)
    class Output(Abstract):
        pass

    @ta.final
    async def execute(self, executor: 'CommandExecutor') -> CommandOutputT:
        return check.isinstance(await executor.execute(self), self.Output)  # type: ignore[return-value]


##


@dc.dataclass(frozen=True)
class CommandException:
    name: str
    repr: str

    traceback: ta.Optional[str] = None

    exc: ta.Optional[ta.Any] = None  # Exception

    cmd: ta.Optional[Command] = None

    @classmethod
    def of(
            cls,
            exc: Exception,
            *,
            omit_exc_object: bool = False,

            cmd: ta.Optional[Command] = None,
    ) -> 'CommandException':
        return CommandException(
            name=type(exc).__qualname__,
            repr=repr(exc),

            traceback=(
                ''.join(traceback.format_tb(exc.__traceback__))
                if getattr(exc, '__traceback__', None) is not None else None
            ),

            exc=None if omit_exc_object else exc,

            cmd=cmd,
        )


class CommandOutputOrException(Abstract, ta.Generic[CommandOutputT]):
    @property
    @abc.abstractmethod
    def output(self) -> ta.Optional[CommandOutputT]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def exception(self) -> ta.Optional[CommandException]:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class CommandOutputOrExceptionData(CommandOutputOrException):
    output: ta.Optional[Command.Output] = None
    exception: ta.Optional[CommandException] = None


class CommandExecutor(Abstract, ta.Generic[CommandT, CommandOutputT]):
    @abc.abstractmethod
    def execute(self, cmd: CommandT) -> ta.Awaitable[CommandOutputT]:
        raise NotImplementedError

    async def try_execute(
            self,
            cmd: CommandT,
            *,
            log: ta.Optional[LoggerLike] = None,
            omit_exc_object: bool = False,
    ) -> CommandOutputOrException[CommandOutputT]:
        try:
            o = await self.execute(cmd)

        except Exception as e:  # noqa
            if log is not None:
                log.exception('Exception executing command: %r', type(cmd))

            return CommandOutputOrExceptionData(exception=CommandException.of(
                e,
                omit_exc_object=omit_exc_object,
                cmd=cmd,
            ))

        else:
            return CommandOutputOrExceptionData(output=o)


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
