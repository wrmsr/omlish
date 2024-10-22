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
import dataclasses as dc
import queue
import threading
import time
import typing as ta

import httpx

from omdev.secrets import load_secrets
from ominfra.clouds.aws.auth import V4AwsSigner
from ominfra.clouds.aws.logs import AwsLogEvent
from ominfra.clouds.aws.logs import AwsPutLogEventsRequest
from ominfra.clouds.aws.logs import AwsPutLogEventsResponse
from omlish.formats import json
from omlish.lite.check import check_isinstance
from omlish.lite.io import DelimitingBuffer


##


@dc.dataclass
class JournalctlOpts:
    after_cursor: ta.Optional[str] = None

    since: ta.Optional[str] = None
    until: ta.Optional[str] = None


class JournalctlMessageBuilder:
    def __init__(
            self,
            opts: JournalctlOpts,
    ) -> None:
        super().__init__()

        self._opts = opts
        self._buf = DelimitingBuffer(b'\n')

    @dc.dataclass(frozen=True)
    class Message:
        raw: bytes
        dct: ta.Mapping[str, ta.Any]
        cursor: str

    def _make_message(self, raw: bytes) -> Message:
        dct = json.loads(raw.decode('utf-8', 'replace'))
        try:
            cursor = dct['__CURSOR']
        except KeyError:
            raise Exception(f'No cursor present: {raw!r}')
        return JournalctlMessageBuilder.Message(
            raw=raw,
            dct=dct,
            cursor=cursor,
        )

    def feed(self, data: bytes) -> ta.Sequence[Message]:
        ret: ta.List[JournalctlMessageBuilder.Message] = []
        for line in self._buf.feed(data):
            ret.append(self._make_message(check_isinstance(line, bytes)))
        return ret


class ThreadWorker:
    def __init__(
            self,
            *,
            stop_event: ta.Optional[threading.Event] = None,
    ) -> None:
        super().__init__()

        if stop_event is None:
            stop_event = threading.Event()
        self._stop_event = stop_event

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass


class JournalctlTailerWorker(ThreadWorker):
    def __init__(
            self,
            output: queue.Queue,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)
        self._output = output


##


def _main() -> None:
    payload = AwsPutLogEventsRequest(
        log_group_name='omlish',
        log_stream_name='test',
        log_events=[
            AwsLogEvent(
                timestamp=int(time.time() * 1000.),
                message=f'Test log message {time.time()}',
            ),
        ],
    )

    body = json.dumps_compact(payload.to_aws()).encode('utf-8')

    url = 'https://logs.us-west-1.amazonaws.com/'

    headers = {
        'X-Amz-Target': ['Logs_20140328.PutLogEvents'],
        'Content-Type': ['application/x-amz-json-1.1'],
    }

    region_name = 'us-west-1'
    service_name = 'logs'

    #

    req = V4AwsSigner.Request(
        method='POST',
        url=url,
        headers=headers,
        payload=body,
    )

    #

    secrets = load_secrets()

    creds = V4AwsSigner.Credentials(
        secrets.get('aws_access_key_id').reveal(),
        secrets.get('aws_secret_access_key').reveal(),
    )

    #

    sig_headers = V4AwsSigner(
        creds,
        region_name,
        service_name,
    ).sign(
        req,
        sign_payload=False,
    )
    req = dc.replace(req, headers={**req.headers, **sig_headers})

    resp = httpx.post(
        req.url,
        headers=[(k, v) for k, vs in req.headers.items() for v in vs],
        follow_redirects=True,
        content=req.payload,
    )

    print((resp, resp.content))

    response = AwsPutLogEventsResponse.from_aws(resp.json())
    print(response)


if __name__ == '__main__':
    _main()
