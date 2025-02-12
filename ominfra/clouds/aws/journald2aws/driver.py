# ruff: noqa: UP007
"""
TODO:
 - create log group
 - log stats - chunk sizes, byte count, num calls, etc

==

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
import dataclasses as dc
import os.path
import queue
import time
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.contextmanagers import ExitStacked
from omlish.lite.logs import log
from omlish.lite.runtime import is_debugger_attached
from omlish.os.pidfiles.pidfile import Pidfile

from ....journald.messages import JournalctlMessage  # noqa
from ....journald.tailer import JournalctlTailerWorker
from ....threadworkers import ThreadWorkerGroup
from ..auth import AwsSigner
from ..logs import AwsLogMessageBuilder
from .cursor import JournalctlToAwsCursor
from .poster import JournalctlToAwsPosterWorker


##


class JournalctlToAwsDriver(ExitStacked):
    @dc.dataclass(frozen=True)
    class Config:
        pid_file: ta.Optional[str] = None

        cursor_file: ta.Optional[str] = None

        runtime_limit: ta.Optional[float] = None
        heartbeat_age_limit: ta.Optional[float] = 60.

        #

        aws_log_group_name: str = 'omlish'
        aws_log_stream_name: ta.Optional[str] = None

        aws_access_key_id: ta.Optional[str] = None
        aws_secret_access_key: ta.Optional[str] = dc.field(default=None, repr=False)

        aws_region_name: str = 'us-west-1'

        aws_dry_run: bool = False

        #

        journalctl_cmd: ta.Optional[ta.Sequence[str]] = None

        journalctl_after_cursor: ta.Optional[str] = None
        journalctl_since: ta.Optional[str] = None

    def __init__(self, config: Config) -> None:
        super().__init__()

        self._config = config

    #

    @cached_nullary
    def _pidfile(self) -> ta.Optional[Pidfile]:
        if self._config.pid_file is None:
            return None

        pfp = os.path.expanduser(self._config.pid_file)

        log.info('Opening pidfile %s', pfp)

        pf = self._enter_context(Pidfile(pfp))
        pf.write()
        return pf

    def _ensure_locked(self) -> None:
        if (pf := self._pidfile()) is not None:
            pf.acquire_lock()

    #

    @cached_nullary
    def _cursor(self) -> JournalctlToAwsCursor:
        return JournalctlToAwsCursor(
            self._config.cursor_file,
            ensure_locked=self._ensure_locked,
        )

    #

    @cached_nullary
    def _aws_credentials(self) -> ta.Optional[AwsSigner.Credentials]:
        if self._config.aws_access_key_id is None and self._config.aws_secret_access_key is None:
            return None

        return AwsSigner.Credentials(
            access_key_id=check.non_empty_str(self._config.aws_access_key_id),
            secret_access_key=check.non_empty_str(self._config.aws_secret_access_key),
        )

    @cached_nullary
    def _aws_log_message_builder(self) -> AwsLogMessageBuilder:
        return AwsLogMessageBuilder(
            log_group_name=self._config.aws_log_group_name,
            log_stream_name=check.non_empty_str(self._config.aws_log_stream_name),
            region_name=self._config.aws_region_name,
            credentials=self._aws_credentials(),
        )

    #

    @cached_nullary
    def _worker_group(self) -> ThreadWorkerGroup:
        return ThreadWorkerGroup()

    #

    @cached_nullary
    def _journalctl_message_queue(self):  # type: () -> queue.Queue[ta.Sequence[JournalctlMessage]]
        return queue.Queue()

    @cached_nullary
    def _journalctl_tailer_worker(self) -> JournalctlTailerWorker:
        ac: ta.Optional[str] = None

        if (since := self._config.journalctl_since):
            log.info('Starting since %s', since)

        else:
            ac = self._config.journalctl_after_cursor
            if ac is None:
                ac = self._cursor().get()
            if ac is not None:
                log.info('Starting from cursor %s', ac)

        return JournalctlTailerWorker(
            self._journalctl_message_queue(),

            since=since,
            after_cursor=ac,

            cmd=self._config.journalctl_cmd,
            shell_wrap=is_debugger_attached(),

            worker_groups=[self._worker_group()],
        )

    #

    @cached_nullary
    def _aws_poster_worker(self) -> JournalctlToAwsPosterWorker:
        return JournalctlToAwsPosterWorker(
            self._journalctl_message_queue(),
            self._aws_log_message_builder(),
            self._cursor(),

            ensure_locked=self._ensure_locked,
            dry_run=self._config.aws_dry_run,

            worker_groups=[self._worker_group()],
        )

    #

    def _exit_contexts(self) -> None:
        wg = self._worker_group()
        wg.stop_all()
        wg.join_all()

    def run(self) -> None:
        self._aws_poster_worker()
        self._journalctl_tailer_worker()

        wg = self._worker_group()
        wg.start_all()

        start = time.time()

        while True:
            for w in wg.get_dead():
                log.critical('Worker died: %r', w)
                break

            if (al := self._config.heartbeat_age_limit) is not None:
                hbs = wg.check_heartbeats()
                log.debug('Worker heartbeats: %r', hbs)
                for w, age in hbs.items():
                    if age > al:
                        log.critical('Worker heartbeat age limit exceeded: %r %f > %f', w, age, al)
                        break

            if (rl := self._config.runtime_limit) is not None and time.time() - start >= rl:
                log.warning('Runtime limit reached')
                break

            time.sleep(1.)

        wg.stop_all()
        wg.join_all()
