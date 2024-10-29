# ruff: noqa: UP007
import fcntl
import os.path
import queue  # noqa
import subprocess
import time
import typing as ta

from omlish.lite.check import check_not_none
from omlish.lite.logs import log
from omlish.lite.subprocesses import subprocess_shell_wrap_exec

from ..threadworker import ThreadWorker
from .messages import JournalctlMessage  # noqa
from .messages import JournalctlMessageBuilder


class JournalctlTailerWorker(ThreadWorker):
    DEFAULT_CMD: ta.ClassVar[ta.Sequence[str]] = ['journalctl']

    def __init__(
            self,
            output,  # type: queue.Queue[ta.Sequence[JournalctlMessage]]
            *,
            cmd: ta.Optional[ta.Sequence[str]] = None,
            since: ta.Optional[str] = None,
            after_cursor: ta.Optional[str] = None,
            shell_wrap: bool = False,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._output = output
        self._cmd = cmd or self.DEFAULT_CMD
        self._since = since
        self._after_cursor = after_cursor
        self._shell_wrap = shell_wrap

        self._mb = JournalctlMessageBuilder()

        self._proc: ta.Optional[subprocess.Popen] = None

    def _run(self) -> None:
        cmd = [
            *self._cmd,
            '--output', 'json',
            '--show-cursor',
            '--follow',
        ]

        if self._since is not None:
            cmd.extend(['--since', self._since])

        if self._after_cursor is not None:
            cmd.extend(['--after-cursor', self._after_cursor])

        if self._shell_wrap:
            cmd = list(subprocess_shell_wrap_exec(*cmd))

        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
        ) as self._proc:
            stdout = check_not_none(self._proc.stdout)

            fd = stdout.fileno()
            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

            while True:
                while stdout.readable():
                    buf = stdout.read(53)
                    if not buf:
                        log.debug('Empty read')
                        break

                    log.debug('Read buffer: %r', buf)
                    msgs = self._mb.feed(buf)
                    if msgs:
                        self._output.put(msgs)

                if self._proc.poll() is not None:
                    log.debug('Process terminated')
                    break

                log.debug('Not readable')
                time.sleep(1)
