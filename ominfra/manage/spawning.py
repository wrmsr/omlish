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

    @dc.dataclass(frozen=True)
    class Spawned:
        stdin: ta.IO
        stdout: ta.IO
        stderr: ta.Optional[ta.IO]

    _STDERR_KWARG_MAP: ta.Mapping[str, int] = {
        'pipe': subprocess.PIPE,
        'stdout': subprocess.STDOUT,
        'devnull': subprocess.DEVNULL,
    }

    @contextlib.contextmanager
    def spawn(self) -> ta.Generator[Spawned, None, None]:
        if self._shell is not None:
            sh_src = f'{self._python} -c {shlex.quote(self._src)}'
            if self._shell_quote:
                sh_src = shlex.quote(sh_src)
            sh_cmd = f'{self._shell} {sh_src}'
            cmd = [sh_cmd]
            shell = True
        else:
            cmd = [self._python, '-c', self._src]
            shell = False

        with subprocess.Popen(
            subprocess_maybe_shell_wrap_exec(*cmd),
            shell=shell,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=self._STDERR_KWARG_MAP[self._stderr] if self._stderr is not None else None,
        ) as proc:
            yield PySpawner.Spawned(
                stdin=check_not_none(proc.stdin),
                stdout=check_not_none(proc.stdout),
                stderr=proc.stderr,
            )

