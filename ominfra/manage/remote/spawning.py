# ruff: noqa: UP006 UP007
import abc
import asyncio
import contextlib
import dataclasses as dc
import shlex
import subprocess
import typing as ta

from omlish.lite.asyncio.subprocesses import asyncio_subprocess_popen
from omlish.lite.check import check_not_none
from omlish.lite.subprocesses import SUBPROCESS_CHANNEL_OPTION_VALUES
from omlish.lite.subprocesses import SubprocessChannelOption
from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec


##


class RemoteSpawning(abc.ABC):
    @dc.dataclass(frozen=True)
    class Target:
        shell: ta.Optional[str] = None
        shell_quote: bool = False

        DEFAULT_PYTHON: ta.ClassVar[str] = 'python3'
        python: str = DEFAULT_PYTHON

        stderr: ta.Optional[str] = None  # SubprocessChannelOption

    @dc.dataclass(frozen=True)
    class Spawned:
        stdin: asyncio.StreamWriter
        stdout: asyncio.StreamReader
        stderr: ta.Optional[asyncio.StreamReader]

    @abc.abstractmethod
    def spawn(
            self,
            tgt: Target,
            src: str,
            *,
            timeout: ta.Optional[float] = None,
            debug: bool = False,
    ) -> ta.AsyncContextManager[Spawned]:
        raise NotImplementedError


##


class SubprocessRemoteSpawning(RemoteSpawning):
    class _PreparedCmd(ta.NamedTuple):  # noqa
        cmd: ta.Sequence[str]
        shell: bool

    def _prepare_cmd(
            self,
            tgt: RemoteSpawning.Target,
            src: str,
    ) -> _PreparedCmd:
        if tgt.shell is not None:
            sh_src = f'{tgt.python} -c {shlex.quote(src)}'
            if tgt.shell_quote:
                sh_src = shlex.quote(sh_src)
            sh_cmd = f'{tgt.shell} {sh_src}'
            return SubprocessRemoteSpawning._PreparedCmd([sh_cmd], shell=True)

        else:
            return SubprocessRemoteSpawning._PreparedCmd([tgt.python, '-c', src], shell=False)

    #

    @contextlib.asynccontextmanager
    async def spawn(
            self,
            tgt: RemoteSpawning.Target,
            src: str,
            *,
            timeout: ta.Optional[float] = None,
            debug: bool = False,
    ) -> ta.AsyncGenerator[RemoteSpawning.Spawned, None]:
        pc = self._prepare_cmd(tgt, src)

        cmd = pc.cmd
        if not debug:
            cmd = subprocess_maybe_shell_wrap_exec(*cmd)

        async with asyncio_subprocess_popen(
                *cmd,
                shell=pc.shell,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=(
                    SUBPROCESS_CHANNEL_OPTION_VALUES[ta.cast(SubprocessChannelOption, tgt.stderr)]
                    if tgt.stderr is not None else None
                ),
                timeout=timeout,
        ) as proc:
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
