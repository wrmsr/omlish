# ruff: noqa: UP006 UP007
import contextlib
import dataclasses as dc
import shlex
import subprocess
import typing as ta

from omlish.lite.check import check_not_none
from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec


class PySpawner:
    DEFAULT_PYTHON = 'python3'

    def __init__(
            self,
            src: str,
            *,
            shell: ta.Optional[str] = None,
            shell_quote: bool = False,
            python: str = DEFAULT_PYTHON,
            stderr: ta.Optional[ta.Literal['pipe', 'stdout', 'devnull']] = None,
    ) -> None:
        super().__init__()

        self._src = src
        self._shell = shell
        self._shell_quote = shell_quote
        self._python = python
        self._stderr = stderr

    #

    class _PreparedCmd(ta.NamedTuple):
        cmd: ta.Sequence[str]
        shell: bool

    def _prepare_cmd(self) -> _PreparedCmd:
        if self._shell is not None:
            sh_src = f'{self._python} -c {shlex.quote(self._src)}'
            if self._shell_quote:
                sh_src = shlex.quote(sh_src)
            sh_cmd = f'{self._shell} {sh_src}'
            return PySpawner._PreparedCmd(
                cmd=[sh_cmd],
                shell=True,
            )

        else:
            return PySpawner._PreparedCmd(
                cmd=[self._python, '-c', self._src],
                shell=False,
            )

    #

    _STDERR_KWARG_MAP: ta.Mapping[str, int] = {
        'pipe': subprocess.PIPE,
        'stdout': subprocess.STDOUT,
        'devnull': subprocess.DEVNULL,
    }

    @dc.dataclass(frozen=True)
    class Spawned:
        stdin: ta.IO
        stdout: ta.IO
        stderr: ta.Optional[ta.IO]

    @contextlib.contextmanager
    def spawn(
            self,
            *,
            timeout: ta.Optional[float] = None,
    ) -> ta.Generator[Spawned, None, None]:
        pc = self._prepare_cmd()

        with subprocess.Popen(
            subprocess_maybe_shell_wrap_exec(*pc.cmd),
            shell=pc.shell,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=self._STDERR_KWARG_MAP[self._stderr] if self._stderr is not None else None,
        ) as proc:
            stdin = check_not_none(proc.stdin)
            stdout = check_not_none(proc.stdout)

            try:
                yield PySpawner.Spawned(
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
