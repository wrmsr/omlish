# ruff: noqa: TC003 UP006 UP007
import asyncio.subprocess
import dataclasses as dc
import os
import subprocess
import time
import typing as ta

from omlish.lite.asyncio.subprocesses import asyncio_subprocess_communicate
from omlish.lite.asyncio.subprocesses import asyncio_subprocess_popen
from omlish.lite.check import check_not_isinstance
from omlish.lite.check import check_not_none
from omlish.lite.subprocesses import SUBPROCESS_CHANNEL_OPTION_VALUES
from omlish.lite.subprocesses import SubprocessChannelOption
from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec

from .base import Command
from .base import CommandExecutor


##


@dc.dataclass(frozen=True)
class SubprocessCommand(Command['SubprocessCommand.Output']):
    cmd: ta.Sequence[str]

    shell: bool = False
    cwd: ta.Optional[str] = None
    env: ta.Optional[ta.Mapping[str, str]] = None

    stdout: str = 'pipe'  # SubprocessChannelOption
    stderr: str = 'pipe'  # SubprocessChannelOption

    input: ta.Optional[bytes] = None
    timeout: ta.Optional[float] = None

    def __post_init__(self) -> None:
        check_not_isinstance(self.cmd, str)

    @dc.dataclass(frozen=True)
    class Output(Command.Output):
        rc: int
        pid: int

        elapsed_s: float

        stdout: ta.Optional[bytes] = None
        stderr: ta.Optional[bytes] = None


##


class SubprocessCommandExecutor(CommandExecutor[SubprocessCommand, SubprocessCommand.Output]):
    async def execute(self, cmd: SubprocessCommand) -> SubprocessCommand.Output:
        proc: asyncio.subprocess.Process
        async with asyncio_subprocess_popen(
            *subprocess_maybe_shell_wrap_exec(*cmd.cmd),

            shell=cmd.shell,
            cwd=cmd.cwd,
            env={**os.environ, **(cmd.env or {})},

            stdin=subprocess.PIPE if cmd.input is not None else None,
            stdout=SUBPROCESS_CHANNEL_OPTION_VALUES[ta.cast(SubprocessChannelOption, cmd.stdout)],
            stderr=SUBPROCESS_CHANNEL_OPTION_VALUES[ta.cast(SubprocessChannelOption, cmd.stderr)],

            timeout=cmd.timeout,
        ) as proc:
            start_time = time.time()
            stdout, stderr = await asyncio_subprocess_communicate(
                proc,
                input=cmd.input,
                timeout=cmd.timeout,
            )
            end_time = time.time()

        return SubprocessCommand.Output(
            rc=check_not_none(proc.returncode),
            pid=proc.pid,

            elapsed_s=end_time - start_time,

            stdout=stdout,  # noqa
            stderr=stderr,  # noqa
        )
