#!/usr/bin/env python3
# @omlish-amalg ./_manage.py
# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import os
import subprocess
import time
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

        shell: bool = False
        cwd: ta.Optional[str] = None
        env: ta.Optional[ta.Mapping[str, str]] = None

        capture_stdout: bool = False
        capture_stderr: bool = False

        input: ta.Optional[bytes] = None
        timeout: ta.Optional[float] = None

        def __post_init__(self) -> None:
            if isinstance(self.args, str):
                raise TypeError(self.args)

    @dc.dataclass(frozen=True)
    class Output(Command.Output):
        rc: int
        pid: int

        elapsed_s: float

        stdout: ta.Optional[bytes] = None
        stderr: ta.Optional[bytes] = None

    def _execute(self, inp: Input) -> Output:
        proc = subprocess.Popen(
            subprocess_maybe_shell_wrap_exec(*inp.args),

            shell=inp.shell,
            cwd=inp.cwd,
            env={**os.environ, **(inp.env or {})},

            stdin=subprocess.PIPE if inp.input is not None else None,
            stdout=subprocess.PIPE if inp.capture_stdout else None,
            stderr=subprocess.PIPE if inp.capture_stderr else None,
        )

        start_time = time.time()
        stdout, stderr = proc.communicate(
            input=inp.input,
            timeout=inp.timeout,
        )
        end_time = time.time()

        return SubprocessCommand.Output(
            rc=proc.returncode,
            pid=proc.pid,

            elapsed_s=end_time - start_time,

            stdout=stdout,  # noqa
            stderr=stderr,  # noqa
        )


def _main() -> None:
    i = SubprocessCommand.Input(
        args=['python3', '-'],
        input=b'print(1)\n',
        capture_stdout=True,
    )
    o = SubprocessCommand()._execute(i)  # noqa
    print(o)


if __name__ == '__main__':
    _main()
