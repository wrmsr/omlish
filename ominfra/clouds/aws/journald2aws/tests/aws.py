"""
TODO:
 - max_items
 - max_bytes
 - flush_interval
 - !! sort by timestamp
"""
import dataclasses as dc
import json
import typing as ta

from omlish.lite.check import check_non_empty_str
from omlish.lite.check import check_single

from ...auth import AwsSigner
from ...auth import V4AwsSigner
from ...logs import AwsLogEvent
from ...logs import AwsPutLogEventsRequest


class AwsLogMessagePoster:
    DEFAULT_URL = 'https://logs.{region_name}.amazonaws.com/'  # noqa

    DEFAULT_SERVICE_NAME = 'logs'

    DEFAULT_TARGET = 'Logs_20140328.PutLogEvents'
    DEFAULT_CONTENT_TYPE = 'application/x-amz-json-1.1'

    DEFAULT_HEADERS: ta.Mapping[str, str] = {
        'X-Amz-Target': DEFAULT_TARGET,
        'Content-Type': DEFAULT_CONTENT_TYPE,
    }

    def __init__(
            self,
            log_group_name: str,
            log_stream_name: str,
            region_name: str,
            credentials: AwsSigner.Credentials,
            *,
            url: ta.Optional[str] = None,
            service_name: str = DEFAULT_SERVICE_NAME,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            extra_headers: ta.Optional[ta.Mapping[str, str]] = None,
    ) -> None:
        super().__init__()

        self._log_group_name = check_non_empty_str(log_group_name)
        self._log_stream_name = check_non_empty_str(log_stream_name)

        if url is None:
            url = self.DEFAULT_URL.format(region_name=region_name)
        self._url = url

        if headers is None:
            headers = self.DEFAULT_HEADERS
        if extra_headers is not None:
            headers = {**headers, **extra_headers}
        self._headers = headers

        self._signer = V4AwsSigner(
            credentials,
            region_name,
            service_name,
        )

    #

    @dc.dataclass(frozen=True)
    class Message:
        message: str
        ts_ms: int  # milliseconds UTC

    @dc.dataclass(frozen=True)
    class Post:
        url: str
        headers: ta.Mapping[str, str]
        data: bytes

    def feed(self, messages: ta.Sequence[Message]) -> ta.Sequence[Post]:
        if not messages:
            return []

        payload = AwsPutLogEventsRequest(
            log_group_name=self._log_group_name,
            log_stream_name=self._log_stream_name,
            log_events=[
                AwsLogEvent(
                    message=m.message,
                    timestamp=m.ts_ms,
                )
                for m in messages
            ],
        )

        body = json.dumps(
            payload.to_aws(),
            indent=None,
            separators=(',', ':'),
        ).encode('utf-8')

        sig_req = V4AwsSigner.Request(
            method='POST',
            url=self._url,
            headers=self._headers,
            payload=body,
        )

        sig_headers = self._signer.sign(
            sig_req,
            sign_payload=False,
        )
        sig_req = dc.replace(sig_req, headers={**sig_req.headers, **sig_headers})

        post = AwsLogMessagePoster.Post(
            url=self._url,
            headers={k: check_single(v) for k, v in sig_req.headers.items()},
            data=sig_req.payload,
        )

        return [post]
