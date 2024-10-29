#!/usr/bin/env python3
# ruff: noqa: UP006 UP007
# @omlish-amalg ./_journald2aws.py
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
import argparse
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
import urllib.request

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check_non_empty_str
from omlish.lite.check import check_not_none
from omlish.lite.logs import configure_standard_logging
from omlish.lite.logs import log
from omlish.lite.runtime import is_debugger_attached
from omlish.lite.subprocesses import subprocess_shell_wrap_exec

from ...auth import AwsSigner
from ...logs import AwsLogMessagePoster
from ...logs import AwsPutLogEventsResponse
from ..journald import JournalctlMessage  # noqa
from ..journald import JournalctlMessageBuilder


@dc.dataclass(frozen=True)
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


class JournalctlToAws:
    @dc.dataclass(frozen=True)
    class Config:
        aws_log_group_name: str = 'omlish'
        aws_log_stream_name: ta.Optional[str] = None

        aws_access_key: ta.Optional[str] = None
        aws_secret_key: ta.Optional[str] = dc.field(default=None, repr=False)

        aws_region_name: str = 'us-west-1'

        journalctl_cmd_override: ta.Optional[ta.Sequence[str]] = None

        dry_run: bool = False

    def __init__(self, config: Config) -> None:
        super().__init__()
        self._config = config

    @cached_nullary
    def _aws_credentials(self) -> AwsSigner.Credentials:
        return AwsSigner.Credentials(
            access_key=check_non_empty_str(self._config.aws_access_key),
            secret_key=check_non_empty_str(self._config.aws_secret_key),
        )

    @cached_nullary
    def _aws_log_message_poster(self) -> AwsLogMessagePoster:
        return AwsLogMessagePoster(
            log_group_name=self._config.aws_log_group_name,
            log_stream_name=check_non_empty_str(self._config.aws_log_stream_name),
            region_name=self._config.aws_region_name,
            credentials=check_not_none(self._aws_credentials()),
        )

    @cached_nullary
    def _journalctl_message_queue(self):  # type: () -> queue.Queue[ta.Sequence[JournalctlMessage]]
        return queue.Queue()

    @cached_nullary
    def _journalctl_tailer_worker(self) -> JournalctlTailerWorker:
        return JournalctlTailerWorker(
            self._journalctl_message_queue(),
            cmd_override=self._config.journalctl_cmd_override,
            shell_wrap=is_debugger_attached(),
        )

    def run(self) -> None:
        q = self._journalctl_message_queue()
        jtw = self._journalctl_tailer_worker()
        mp = self._aws_log_message_poster()

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

            if not self._config.dry_run:
                with urllib.request.urlopen(urllib.request.Request(  # noqa
                        post.url,
                        method='POST',
                        headers=dict(post.headers),
                        data=post.data,
                )) as resp:
                    response = AwsPutLogEventsResponse.from_aws(json.loads(resp.read().decode('utf-8')))
                print(response)


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--message', nargs='?')
    parser.add_argument('--post', action='store_true')
    parser.add_argument('--real', action='store_true')
    parser.add_argument('--config-json-file')
    args = parser.parse_args()

    #

    configure_standard_logging('DEBUG')

    #

    config: ta.Optional[ta.Mapping[str, ta.Any]] = None
    if args.config_json_file:
        with open(args.config_json_file) as cf:
            config = json.load(cf)

    #

    credentials: ta.Optional[AwsSigner.Credentials] = None

    if credentials is None and config is not None and 'aws_access_key_id' in config:
        credentials = AwsSigner.Credentials(
            config['aws_access_key_id'],
            config['aws_secret_access_key'],
        )
    if credentials is None and 'AWS_ACCESS_KEY_ID' in os.environ:
        credentials = AwsSigner.Credentials(
            os.environ['AWS_ACCESS_KEY_ID'],
            os.environ['AWS_SECRET_ACCESS_KEY'],
        )
    if credentials is None:
        secrets = __import__('omdev.secrets').secrets.load_secrets()
        credentials = AwsSigner.Credentials(
            secrets.get('aws_access_key_id').reveal(),
            secrets.get('aws_secret_access_key').reveal(),
        )

    if credentials is None:
        raise Exception('No credentials found')

    #

    journalctl_cmd_override: ta.Optional[ta.Sequence[str]] = None
    if not args.real:
        journalctl_cmd_override = [
            sys.executable,
            os.path.join(os.path.dirname(__file__), 'genmessages.py'),
            '--sleep-n', '2',
            '--sleep-s', '.5',
            *(['--message', args.message] if args.message else []),
            '1000000',
        ]

    #

    jta = JournalctlToAws(JournalctlToAws.Config(
        aws_log_stream_name='test',
        aws_access_key=credentials.access_key,
        aws_secret_key=credentials.secret_key,
        journalctl_cmd_override=journalctl_cmd_override,
        dry_run=not args.post,
    ))
    jta.run()


if __name__ == '__main__':
    _main()
