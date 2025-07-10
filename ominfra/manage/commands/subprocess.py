# ruff: noqa: TC003 UP006 UP007 UP045
import asyncio.subprocess
import dataclasses as dc
import os
import subprocess
import time
import typing as ta

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.check import check
from omlish.subprocesses.base import SUBPROCESS_CHANNEL_OPTION_VALUES
from omlish.subprocesses.base import SubprocessChannelOption
from omlish.subprocesses.wrap import subprocess_maybe_shell_wrap_exec

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
    decode_stdout: ta.Optional[str] = None

    stderr: str = 'pipe'  # SubprocessChannelOption
    decode_stderr: ta.Optional[str] = None

    input: ta.Optional[bytes] = None
    encode_input: ta.Optional[str] = None
    input_str: ta.Optional[str] = None

    timeout: ta.Optional[float] = None

    def __post_init__(self) -> None:
        check.not_isinstance(self.cmd, str)
        check.state(not (self.input is not None and self.input_str is not None))
        if self.decode_stdout is not None:
            check.non_empty_str(self.decode_stdout)
        if self.decode_stderr is not None:
            check.non_empty_str(self.decode_stderr)
        if self.encode_input is not None:
            check.non_empty_str(self.encode_input)

    @dc.dataclass(frozen=True)
    class Output(Command.Output):
        rc: int
        pid: int

        elapsed_s: float

        stdout: ta.Optional[bytes] = None
        stdout_str: ta.Optional[str] = None

        stderr: ta.Optional[bytes] = None
        stderr_str: ta.Optional[str] = None


class SubprocessCommandExecutor(CommandExecutor[SubprocessCommand, SubprocessCommand.Output]):
    DEFAULT_INPUT_ENCODING: ta.ClassVar[str] = 'utf-8'

    async def execute(self, cmd: SubprocessCommand) -> SubprocessCommand.Output:
        input_bytes: ta.Optional[bytes]
        if cmd.input is not None:
            check.none(cmd.input_str)
            input_bytes = cmd.input
        elif cmd.input_str is not None:
            input_bytes = cmd.input_str.encode(cmd.encode_input or self.DEFAULT_INPUT_ENCODING)
        else:
            input_bytes = None

        proc: asyncio.subprocess.Process
        async with asyncio_subprocesses.popen(
            *subprocess_maybe_shell_wrap_exec(*cmd.cmd),

            shell=cmd.shell,
            cwd=cmd.cwd,
            env={**os.environ, **(cmd.env or {})},

            stdin=subprocess.PIPE if input_bytes is not None else None,
            stdout=SUBPROCESS_CHANNEL_OPTION_VALUES[ta.cast(SubprocessChannelOption, cmd.stdout)],
            stderr=SUBPROCESS_CHANNEL_OPTION_VALUES[ta.cast(SubprocessChannelOption, cmd.stderr)],

            timeout=cmd.timeout,
        ) as proc:
            start_time = time.time()
            stdout, stderr = await asyncio_subprocesses.communicate(
                proc,
                input=input,
                timeout=cmd.timeout,
            )
            end_time = time.time()

        out_kw: ta.Dict[str, ta.Any] = {}
        if stdout is not None:
            if cmd.decode_stdout is not None:
                out_kw.update(stdout_str=stdout.decode(cmd.decode_stdout))
            else:
                out_kw.update(stdout=stdout)
        if stderr is not None:
            if cmd.decode_stderr is not None:
                out_kw.update(stderr_str=stderr.decode(cmd.decode_stderr))
            else:
                out_kw.update(stderr=stderr)

        return SubprocessCommand.Output(
            rc=check.not_none(proc.returncode),
            pid=proc.pid,

            elapsed_s=end_time - start_time,

            **out_kw,
        )
