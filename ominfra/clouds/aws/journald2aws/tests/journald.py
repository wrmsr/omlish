"""
https://www.freedesktop.org/software/systemd/man/latest/journalctl.html

journalctl:
  -o json
  --show-cursor

  --since "2012-10-30 18:17:16"
  --until "2012-10-30 18:17:16"

  --after-cursor <cursor>

==

https://www.freedesktop.org/software/systemd/man/latest/systemd.journal-fields.html
"""
import abc
import dataclasses as dc
import fcntl
import os.path
import queue
import subprocess
import sys
import threading
import time
import typing as ta

from omlish.formats import json
from omlish.lite.check import check_isinstance
from omlish.lite.io import DelimitingBuffer
from omlish.lite.logs import configure_standard_logging
from omlish.lite.logs import log
from omlish.lite.subprocesses import subprocess_shell_wrap_exec


@dc.dataclass
class JournalctlOpts:
    after_cursor: ta.Optional[str] = None

    since: ta.Optional[str] = None
    until: ta.Optional[str] = None


class JournalctlMessageBuilder:
    def __init__(self) -> None:
        super().__init__()

        self._buf = DelimitingBuffer(b'\n')

    @dc.dataclass(frozen=True)
    class Message:
        raw: bytes
        dct: ta.Optional[ta.Mapping[str, ta.Any]] = None
        cursor: ta.Optional[str] = None
        ts_us: ta.Optional[int] = None  # microseconds UTC

    _cursor_field = '__CURSOR'
    _timestamp_field = '_SOURCE_REALTIME_TIMESTAMP'

    def _make_message(self, raw: bytes) -> Message:
        dct = None
        cursor = None
        ts = None

        try:
            dct = json.loads(raw.decode('utf-8', 'replace'))
        except Exception:  # noqa
            log.exception('Failed to parse raw message: %r', raw)

        else:
            cursor = dct.get(self._cursor_field)

            if tsv := dct.get(self._timestamp_field):
                if isinstance(tsv, str):
                    try:
                        ts = int(tsv)
                    except ValueError:
                        try:
                            ts = int(float(tsv))
                        except ValueError:
                            log.exception('Failed to parse timestamp: %r', tsv)
                elif isinstance(tsv, (int, float)):
                    ts = int(tsv)
                else:
                    log.exception('Invalid timestamp: %r', tsv)

        return JournalctlMessageBuilder.Message(
            raw=raw,
            dct=dct,
            cursor=cursor,
            ts_us=ts,
        )

    def feed(self, data: bytes) -> ta.Sequence[Message]:
        ret: ta.List[JournalctlMessageBuilder.Message] = []
        for line in self._buf.feed(data):
            ret.append(self._make_message(check_isinstance(line, bytes)))
        return ret


class ThreadWorker(abc.ABC):
    def __init__(
            self,
            *,
            stop_event: ta.Optional[threading.Event] = None,
    ) -> None:
        super().__init__()

        if stop_event is None:
            stop_event = threading.Event()
        self._stop_event = stop_event

        self._thread: ta.Optional[threading.Thread] = None

    def start(self) -> None:
        thr = threading.Thread(target=self._run)
        self._thread = thr
        thr.start()

    @abc.abstractmethod
    def _run(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError


class JournalctlTailerWorker(ThreadWorker):
    def __init__(
            self,
            output: queue.Queue,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)
        self._output = output

        self._mb = JournalctlMessageBuilder()

    def _run(self) -> None:
        proc = subprocess.Popen(
            subprocess_shell_wrap_exec(
                sys.executable,
                os.path.join(os.path.dirname(__file__), 'genmessages.py'),
                '--sleep-n', '2',
                '--sleep-s', '.5',
                '1000000',
            ),
            stdout=subprocess.PIPE,
        )

        fd = proc.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        while True:
            while proc.stdout.readable():
                buf = proc.stdout.read(53)
                if not buf:
                    log.debug('Empty read')
                    break

                log.debug('Read buffer: %r', buf)
                for msg in self._mb.feed(buf):
                    print(msg)

            if proc.poll() is not None:
                log.debug('Process terminated')
                break

            log.debug('Not readable')
            time.sleep(1)


def _main() -> None:
    configure_standard_logging('INFO')

    q = queue.Queue()
    jtw = JournalctlTailerWorker(q)
    jtw.start()
    while True:
        m = q.get()
        print(m)


if __name__ == '__main__':
    _main()
