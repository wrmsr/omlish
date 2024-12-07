# ruff: noqa: UP006 UP007
import contextlib
import dataclasses as dc
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

    class _PreparedCmd(ta.NamedTuple):
        cmd: ta.Sequence[str]
        shell: bool

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
            return RemoteSpawning._PreparedCmd(
                cmd=[sh_cmd],
                shell=True,
            )

        else:
            return RemoteSpawning._PreparedCmd(
                cmd=[tgt.python, '-c', src],
                shell=False,
            )

    #

    @dc.dataclass(frozen=True)
    class Spawned:
        stdin: ta.IO
        stdout: ta.IO
        stderr: ta.Optional[ta.IO]

    @contextlib.contextmanager
    def spawn(
            self,
            tgt: Target,
            src: str,
            *,
            timeout: ta.Optional[float] = None,
    ) -> ta.Generator[Spawned, None, None]:
        pc = self._prepare_cmd(tgt, src)

        with subprocess.Popen(
            subprocess_maybe_shell_wrap_exec(*pc.cmd),
            shell=pc.shell,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=(
                SUBPROCESS_CHANNEL_OPTION_VALUES[ta.cast(SubprocessChannelOption, tgt.stderr)]
                if tgt.stderr is not None else None
            ),
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

                proc.wait(timeout)
