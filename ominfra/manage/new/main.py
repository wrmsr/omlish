import abc
import dataclasses as dc
import subprocess
import typing as ta

from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec


CommandInputT = ta.TypeVar('CommandInputT', bound='Command.Input')
CommandOutputT = ta.TypeVar('CommandOutputT', bound='Command.Output')


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


class SubprocessCommand(Command['SubprocessCommand.Input', 'SubprocessCommand.Output']):
    @dc.dataclass(frozen=True)
    class Input(Command.Input):
        args: ta.Sequence[str]

        input: ta.Optional[bytes] = None
        timeout: ta.Optional[float] = None

        capture_stdout: bool = False
        capture_stderr: bool = False

        def __post_init__(self) -> None:
            if isinstance(self.args, str):
                raise TypeError(self.args)

    @dc.dataclass(frozen=True)
    class Output(Command.Output):
        rc: int
        pid: int

        stdout: ta.Optional[bytes] = None
        stderr: ta.Optional[bytes] = None

    def _execute(self, inp: Input) -> Output:
        proc = subprocess.Popen(
            inp.args,

            **(dict(stdout=subprocess.PIPE) if inp.capture_stdout else {}),
            **(dict(stderr=subprocess.PIPE) if inp.capture_stderr else {}),
        )

        stdout, stderr = proc.communicate(
            input=inp.input,
            timeout=inp.timeout,
        )

        return SubprocessCommand.Output(
            rc=proc.returncode,
            pid=proc.pid,

            stdout=stdout,  # noqa
            stderr=stderr,  # noqa
        )


def _main() -> None:
    i = SubprocessCommand.Input(
        args=['echo'],
        input=b'hi',
        capture_stdout=True,
    )
    o = SubprocessCommand()._execute(i)  # noqa
    print(o)


if __name__ == '__main__':
    _main()
