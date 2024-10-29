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
    def __init__(
            self,
            output,  # type: queue.Queue[ta.Sequence[JournalctlMessage]]
            *,
            cmd_override: ta.Optional[ta.Sequence[str]] = None,
            shell_wrap: bool = False,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._output = output
        self._cmd_override = cmd_override
        self._shell_wrap = shell_wrap

        self._mb = JournalctlMessageBuilder()

        self._proc: ta.Optional[subprocess.Popen] = None

    def _run(self) -> None:
        if self._cmd_override is not None:
            cmd = self._cmd_override
        else:
            cmd = [
                'journalctl',
                '-o', 'json',
                '--show-cursor',
                '-f',
                '--since', 'today',
            ]

        if self._shell_wrap:
            cmd = subprocess_shell_wrap_exec(*cmd)

        self._proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
        )

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
