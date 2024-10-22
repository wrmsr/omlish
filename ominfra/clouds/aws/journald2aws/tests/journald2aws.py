# ruff: noqa: UP006 UP007
# @omlish-lite
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

==

@dc.dataclass(frozen=True)
class Journald2AwsConfig:
    log_group_name: str
    log_stream_name: str

    aws_batch_size: int = 1_000
    aws_flush_interval_s: float = 1.
"""
import abc
import dataclasses as dc
import fcntl
import json
import os.path
import queue
import subprocess
import sys
import threading
import time
import typing as ta

from ominfra.clouds.aws.auth import AwsSigner
from ominfra.clouds.aws.logs import AwsPutLogEventsResponse
from omlish.lite.check import check_not_none
from omlish.lite.logs import configure_standard_logging
from omlish.lite.logs import log
from omlish.lite.subprocesses import subprocess_shell_wrap_exec

from ...logs import AwsLogMessagePoster
from ..journald import JournalctlMessage  # noqa
from ..journald import JournalctlMessageBuilder


@dc.dataclass
class JournalctlOpts:
    after_cursor: ta.Optional[str] = None

    since: ta.Optional[str] = None
    until: ta.Optional[str] = None


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

    _sleep_s: float = .5

    def start(self) -> None:
        thr = threading.Thread(target=self._run)
        self._thread = thr
        thr.start()

    @abc.abstractmethod
    def _run(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError

    def cleanup(self) -> None:  # noqa
        pass


class JournalctlTailerWorker(ThreadWorker):
    def __init__(
            self,
            output,  # type: queue.Queue[ta.Sequence[JournalctlMessage]]
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)
        self._output = output

        self._mb = JournalctlMessageBuilder()

        self._proc: ta.Optional[subprocess.Popen] = None

    def _run(self) -> None:
        self._proc = subprocess.Popen(
            subprocess_shell_wrap_exec(
                sys.executable,
                os.path.join(os.path.dirname(__file__), 'genmessages.py'),
                '--sleep-n', '2',
                '--sleep-s', '.5',
                '1000000',
            ),
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


def _main() -> None:
    do_post = False
    # do_post = True

    configure_standard_logging('INFO')

    secrets = __import__('omdev.secrets').secrets.load_secrets()

    mp = AwsLogMessagePoster(
        log_group_name='omlish',
        log_stream_name='test',
        region_name='us-west-1',
        credentials=AwsSigner.Credentials(
            secrets.get('aws_access_key_id').reveal(),
            secrets.get('aws_secret_access_key').reveal(),
        ),
    )

    q = queue.Queue()  # type: queue.Queue[ta.Sequence[JournalctlMessage]]
    jtw = JournalctlTailerWorker(q)
    jtw.start()
    while True:
        msgs = q.get()
        print(msgs)

        if not msgs:
            log.warning('Empty queue chunk')
            continue

        [post] = mp.feed([mp.Message(
            message=json.dumps(m.dct),
            ts_ms=int(time.time() * 1000.),
        ) for m in msgs])
        print(post)

        if do_post:
            resp = __import__('httpx').post(
                post.url,
                headers=post.headers,
                follow_redirects=True,
                content=post.data,
            )

            response = AwsPutLogEventsResponse.from_aws(resp.json())
            print(response)


if __name__ == '__main__':
    _main()
