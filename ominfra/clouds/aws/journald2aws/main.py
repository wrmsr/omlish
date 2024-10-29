#!/usr/bin/env python3
# ruff: noqa: UP007
# @omlish-amalg ../../../scripts/journald2aws.py
"""
TODO:
 - create log group
 - log stats - chunk sizes etc

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
import argparse
import contextlib
import dataclasses as dc
import json
import os.path
import queue
import sys
import time
import typing as ta
import urllib.request

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check_non_empty_str
from omlish.lite.check import check_not_none
from omlish.lite.logs import configure_standard_logging
from omlish.lite.logs import log
from omlish.lite.marshal import unmarshal_obj
from omlish.lite.pidfile import Pidfile
from omlish.lite.runtime import is_debugger_attached

from ..auth import AwsSigner
from ..logs import AwsLogMessagePoster
from ..logs import AwsPutLogEventsResponse
from .journald.messages import JournalctlMessage  # noqa
from .journald.tailer import JournalctlTailerWorker


@dc.dataclass(frozen=True)
class JournalctlOpts:
    after_cursor: ta.Optional[str] = None

    since: ta.Optional[str] = None
    until: ta.Optional[str] = None


class JournalctlToAws:
    @dc.dataclass(frozen=True)
    class Config:
        pid_file: ta.Optional[str] = None

        cursor_file: ta.Optional[str] = None

        #

        aws_log_group_name: str = 'omlish'
        aws_log_stream_name: ta.Optional[str] = None

        aws_access_key_id: ta.Optional[str] = None
        aws_secret_access_key: ta.Optional[str] = dc.field(default=None, repr=False)

        aws_region_name: str = 'us-west-1'

        #

        journalctl_cmd: ta.Optional[ta.Sequence[str]] = None

        journalctl_after_cursor: ta.Optional[str] = None
        journalctl_since: ta.Optional[str] = None

        #

        dry_run: bool = False

    def __init__(self, config: Config) -> None:
        super().__init__()
        self._config = config

    #

    _es: contextlib.ExitStack

    def __enter__(self) -> 'JournalctlToAws':
        self._es = contextlib.ExitStack().__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._es.__exit__(exc_type, exc_val, exc_tb)

    #

    @cached_nullary
    def _pidfile(self) -> ta.Optional[Pidfile]:
        if self._config.pid_file is None:
            return None

        pfp = os.path.expanduser(self._config.pid_file)

        log.info('Opening pidfile %s', pfp)

        pf = self._es.enter_context(Pidfile(pfp))
        pf.write()
        return pf

    def _ensure_locked(self) -> None:
        if (pf := self._pidfile()) is not None:
            pf.ensure_locked()

    #

    def _read_cursor_file(self) -> ta.Optional[str]:
        self._ensure_locked()

        if not (cf := self._config.cursor_file):
            return None
        cf = os.path.expanduser(cf)

        try:
            with open(cf) as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def _write_cursor_file(self, cursor: str) -> None:
        self._ensure_locked()

        if not (cf := self._config.cursor_file):
            return
        cf = os.path.expanduser(cf)

        log.info('Writing cursor file %s : %s', cf, cursor)
        with open(ncf := cf + '.next', 'w') as f:
            f.write(cursor)

        os.rename(ncf, cf)

    #

    @cached_nullary
    def _aws_credentials(self) -> AwsSigner.Credentials:
        return AwsSigner.Credentials(
            access_key_id=check_non_empty_str(self._config.aws_access_key_id),
            secret_access_key=check_non_empty_str(self._config.aws_secret_access_key),
        )

    @cached_nullary
    def _aws_log_message_poster(self) -> AwsLogMessagePoster:
        return AwsLogMessagePoster(
            log_group_name=self._config.aws_log_group_name,
            log_stream_name=check_non_empty_str(self._config.aws_log_stream_name),
            region_name=self._config.aws_region_name,
            credentials=check_not_none(self._aws_credentials()),
        )

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
                ac = self._read_cursor_file()
            if ac is not None:
                log.info('Starting from cursor %s', ac)

        return JournalctlTailerWorker(
            self._journalctl_message_queue(),

            since=since,
            after_cursor=ac,

            cmd=self._config.journalctl_cmd,
            shell_wrap=is_debugger_attached(),
        )

    #

    def run(self) -> None:
        self._ensure_locked()

        q = self._journalctl_message_queue()  # type: queue.Queue[ta.Sequence[JournalctlMessage]]
        jtw = self._journalctl_tailer_worker()  # type: JournalctlTailerWorker
        mp = self._aws_log_message_poster()  # type: AwsLogMessagePoster

        jtw.start()

        last_cursor: ta.Optional[str] = None  # noqa
        while True:
            if not jtw.is_alive():
                log.critical('Journalctl tailer worker died')
                break

            try:
                msgs: ta.Sequence[JournalctlMessage] = q.get(timeout=1.)
            except queue.Empty:
                msgs = []
            if not msgs:
                continue

            log.debug('%r', msgs)

            cur_cursor: ta.Optional[str] = None
            for m in reversed(msgs):
                if m.cursor is not None:
                    cur_cursor = m.cursor
                    break

            if not msgs:
                log.warning('Empty queue chunk')
                continue

            feed_msgs = []
            for m in msgs:
                feed_msgs.append(mp.Message(
                    message=json.dumps(m.dct),
                    ts_ms=int((m.ts_us / 1000.) if m.ts_us is not None else (time.time() * 1000.)),
                ))

            [post] = mp.feed(feed_msgs)
            log.debug('%r', post)

            if not self._config.dry_run:
                with urllib.request.urlopen(urllib.request.Request(  # noqa
                        post.url,
                        method='POST',
                        headers=dict(post.headers),
                        data=post.data,
                )) as resp:
                    response = AwsPutLogEventsResponse.from_aws(json.loads(resp.read().decode('utf-8')))
                log.debug('%r', response)

            if cur_cursor is not None:
                self._write_cursor_file(cur_cursor)
                last_cursor = cur_cursor  # noqa


def _main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('--config-file')
    parser.add_argument('-v', '--verbose', action='store_true')

    parser.add_argument('--after-cursor', nargs='?')
    parser.add_argument('--since', nargs='?')
    parser.add_argument('--dry-run', action='store_true')

    parser.add_argument('--message', nargs='?')
    parser.add_argument('--real', action='store_true')

    args = parser.parse_args()

    #

    configure_standard_logging('DEBUG' if args.verbose else 'INFO')

    #

    config: JournalctlToAws.Config
    if args.config_file:
        with open(os.path.expanduser(args.config_file)) as cf:
            config_dct = json.load(cf)
        config = unmarshal_obj(config_dct, JournalctlToAws.Config)
    else:
        config = JournalctlToAws.Config()

    #

    for k in ['aws_access_key_id', 'aws_secret_access_key']:
        if not getattr(config, k) and k.upper() in os.environ:
            config = dc.replace(config, **{k: os.environ.get(k.upper())})  # type: ignore

    #

    if not args.real:
        config = dc.replace(config, journalctl_cmd=[
            sys.executable,
            os.path.join(os.path.dirname(__file__), 'journald', 'genmessages.py'),
            '--sleep-n', '2',
            '--sleep-s', '.5',
            *(['--message', args.message] if args.message else []),
            '100000',
        ])

    #

    for ca, pa in [
        ('journalctl_after_cursor', 'after_cursor'),
        ('journalctl_since', 'since'),
        ('dry_run', 'dry_run'),
    ]:
        if (av := getattr(args, pa)):
            config = dc.replace(config, **{ca: av})

    #

    with JournalctlToAws(config) as jta:
        jta.run()


if __name__ == '__main__':
    _main()
