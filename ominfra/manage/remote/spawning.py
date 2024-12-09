# ruff: noqa: UP006 UP007
import abc
import asyncio
import contextlib
import dataclasses as dc
import functools
import shlex
import subprocess
import typing as ta

from omlish.lite.check import check_not_none
from omlish.lite.subprocesses import SUBPROCESS_CHANNEL_OPTION_VALUES
from omlish.lite.subprocesses import SubprocessChannelOption
from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec


class RemoteSpawning:
    @dc.dataclass(frozen=True)
    class Target:
        shell: ta.Optional[str] = None
        shell_quote: bool = False

        DEFAULT_PYTHON: ta.ClassVar[str] = 'python3'
        python: str = DEFAULT_PYTHON

        stderr: ta.Optional[str] = None  # SubprocessChannelOption

    #

    class _PreparedCmd(abc.ABC):
        pass

    @dc.dataclass(frozen=True)
    class _ExecPreparedCmd(_PreparedCmd):
        cmd: ta.Sequence[str]

    @dc.dataclass(frozen=True)
    class _ShellPreparedCmd(_PreparedCmd):
        cmd: str

    def _prepare_cmd(
            self,
            tgt: Target,
            src: str,
    ) -> _PreparedCmd:
        if tgt.shell is not None:
            sh_src = f'{tgt.python} -c {shlex.quote(src)}'
            if tgt.shell_quote:
                sh_src = shlex.quote(sh_src)
            sh_cmd = f'{tgt.shell} {sh_src}'
            return RemoteSpawning._ShellPreparedCmd(sh_cmd)

        else:
            return RemoteSpawning._ExecPreparedCmd([tgt.python, '-c', src])

    #

    @dc.dataclass(frozen=True)
    class Spawned:
        stdin: asyncio.StreamWriter
        stdout: asyncio.StreamReader
        stderr: ta.Optional[asyncio.StreamReader]

    @contextlib.asynccontextmanager
    async def spawn(
            self,
            tgt: Target,
            src: str,
            *,
            timeout: ta.Optional[float] = None,
    ) -> ta.Generator[Spawned, None, None]:
        pc = self._prepare_cmd(tgt, src)
        fac: ta.Any
        if isinstance(pc, RemoteSpawning._ExecPreparedCmd):
            fac = functools.partial(
                asyncio.create_subprocess_exec,
                *subprocess_maybe_shell_wrap_exec(*pc.cmd),
            )
        elif isinstance(pc, RemoteSpawning._ShellPreparedCmd):
            fac = functools.partial(
                asyncio.create_subprocess_shell,
                pc.cmd,
            )
        else:
            raise TypeError(pc)

        proc: asyncio.subprocess.Process
        proc = await fac(
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=(
                SUBPROCESS_CHANNEL_OPTION_VALUES[ta.cast(SubprocessChannelOption, tgt.stderr)]
                if tgt.stderr is not None else None
            ),
        )
        try:
            stdin = check_not_none(proc.stdin)
            stdout = check_not_none(proc.stdout)

            try:
                yield RemoteSpawning.Spawned(
                    stdin=stdin,
                    stdout=stdout,
                    stderr=proc.stderr,
                )

            finally:
                try:
                    stdin.close()
                except BrokenPipeError:
                    pass

        finally:
            if timeout:
                await asyncio.wait_for(proc.wait(), timeout=timeout)
            else:
                await proc.wait()
