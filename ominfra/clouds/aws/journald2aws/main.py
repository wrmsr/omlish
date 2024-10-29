#!/usr/bin/env python3
# ruff: noqa: UP007
# @omlish-amalg ./_journald2aws.py
"""
TODO:
 - cursorfile
 - lockfile

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
        pidfile: ta.Optional[str] = None

        aws_log_group_name: str = 'omlish'
        aws_log_stream_name: ta.Optional[str] = None

        aws_access_key_id: ta.Optional[str] = None
        aws_secret_access_key: ta.Optional[str] = dc.field(default=None, repr=False)

        aws_region_name: str = 'us-west-1'

        journalctl_cmd: ta.Optional[ta.Sequence[str]] = None

        dry_run: bool = False

    def __init__(self, config: Config) -> None:
        super().__init__()
        self._config = config

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
        return JournalctlTailerWorker(
            self._journalctl_message_queue(),
            cmd=self._config.journalctl_cmd,
            shell_wrap=is_debugger_attached(),
        )

    #

    def run(self) -> None:
        with contextlib.ExitStack() as es:
            if self._config.pidfile is not None:
                pfp = os.path.expanduser(self._config.pidfile)
                log.info('Opening pidfile %s', pfp)
                pf = es.enter_context(Pidfile(pfp))
                pf.write()

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
    parser.add_argument('--config-file')
    args = parser.parse_args()

    #

    configure_standard_logging('DEBUG')

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
            '1000000',
        ])
    #

    if args.post is not None:
        config = dc.replace(config, dry_run=not args.post)

    #

    jta = JournalctlToAws(config)
    jta.run()


if __name__ == '__main__':
    _main()
