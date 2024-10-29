# ruff: noqa: UP007
import fcntl
import os.path
import queue  # noqa
import subprocess
import time
import typing as ta

from omlish.lite.cached import cached_nullary
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
            since: ta.Optional[str] = None,
            after_cursor: ta.Optional[str] = None,

            cmd: ta.Optional[ta.Sequence[str]] = None,
            shell_wrap: bool = False,

            read_size: int = 0x4000,
            sleep_s: float = 1.,

            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._output = output

        self._since = since
        self._after_cursor = after_cursor

        self._cmd = cmd or self.DEFAULT_CMD
        self._shell_wrap = shell_wrap

        self._read_size = read_size
        self._sleep_s = sleep_s

        self._mb = JournalctlMessageBuilder()

        self._proc: ta.Optional[subprocess.Popen] = None

    @cached_nullary
    def _full_cmd(self) -> ta.Sequence[str]:
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

        return cmd

    def _run(self) -> None:
        with subprocess.Popen(
            self._full_cmd(),
            stdout=subprocess.PIPE,
        ) as self._proc:
            stdout = check_not_none(self._proc.stdout)

            fd = stdout.fileno()
            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

            while True:
                if not self._heartbeat():
                    return

                while stdout.readable():
                    if not self._heartbeat():
                        return

                    buf = stdout.read(self._read_size)
                    if not buf:
                        log.debug('Journalctl empty read')
                        continue

                    log.debug('Journalctl read buffer: %r', buf)
                    msgs = self._mb.feed(buf)
                    if msgs:
                        while True:
                            try:
                                self._output.put(msgs, timeout=1.)
                            except queue.Full:
                                if not self._heartbeat():
                                    return
                            else:
                                break

                if self._proc.poll() is not None:
                    log.critical('Journalctl process terminated')
                    return

                log.debug('Journalctl readable')
                time.sleep(self._sleep_s)
