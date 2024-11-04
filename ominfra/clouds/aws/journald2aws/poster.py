# ruff: noqa: UP007
"""
TODO:
 - retries
"""
import json
import queue
import time
import typing as ta
import urllib.request

from omlish.lite.logs import log

from ....journald.messages import JournalctlMessage  # noqa
from ....threadworkers import ThreadWorker
from ..logs import AwsLogMessageBuilder
from ..logs import AwsPutLogEventsResponse
from .cursor import JournalctlToAwsCursor


class JournalctlToAwsPosterWorker(ThreadWorker):
    def __init__(
            self,
            queue,  # type: queue.Queue[ta.Sequence[JournalctlMessage]]  # noqa
            builder: AwsLogMessageBuilder,
            cursor: JournalctlToAwsCursor,
            *,
            ensure_locked: ta.Optional[ta.Callable[[], None]] = None,
            dry_run: bool = False,
            queue_timeout_s: float = 1.,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)
        self._queue = queue
        self._builder = builder
        self._cursor = cursor
        self._ensure_locked = ensure_locked
        self._dry_run = dry_run
        self._queue_timeout_s = queue_timeout_s
    #

    def _run(self) -> None:
        if self._ensure_locked is not None:
            self._ensure_locked()

        last_cursor: ta.Optional[str] = None  # noqa
        while True:
            self._heartbeat()

            try:
                msgs: ta.Sequence[JournalctlMessage] = self._queue.get(timeout=self._queue_timeout_s)
            except queue.Empty:
                msgs = []

            if not msgs:
                log.debug('Empty queue chunk')
                continue

            log.debug('%r', msgs)

            cur_cursor: ta.Optional[str] = None
            for m in reversed(msgs):
                if m.cursor is not None:
                    cur_cursor = m.cursor
                    break

            feed_msgs = []
            for m in msgs:
                feed_msgs.append(AwsLogMessageBuilder.Message(
                    message=json.dumps(m.dct, sort_keys=True),
                    ts_ms=int((m.ts_us / 1000.) if m.ts_us is not None else (time.time() * 1000.)),
                ))

            for post in self._builder.feed(feed_msgs):
                log.debug('%r', post)

                if not self._dry_run:
                    with urllib.request.urlopen(urllib.request.Request(  # noqa
                            post.url,
                            method='POST',
                            headers=dict(post.headers),
                            data=post.data,
                    )) as resp:
                        response = AwsPutLogEventsResponse.from_aws(json.loads(resp.read().decode('utf-8')))
                    log.debug('%r', response)

            if cur_cursor is not None:
                self._cursor.set(cur_cursor)
                last_cursor = cur_cursor  # noqa
