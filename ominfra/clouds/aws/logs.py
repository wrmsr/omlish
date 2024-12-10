# @omlish-lite
# ruff: noqa: UP007
"""
https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutLogEvents.html :
 - The maximum batch size is 1,048,576 bytes. This size is calculated as the sum of all event messages in UTF-8, plus 26
   bytes for each log event.
 - None of the log events in the batch can be more than 2 hours in the future.
 - None of the log events in the batch can be more than 14 days in the past. Also, none of the log events can be from
   earlier than the retention period of the log group.
 - The log events in the batch must be in chronological order by their timestamp. The timestamp is the time that the
   event occurred, expressed as the number of milliseconds after Jan 1, 1970 00:00:00 UTC. (In AWS Tools for PowerShell
   and the AWS SDK for .NET, the timestamp is specified in .NET format: yyyy-mm-ddThh:mm:ss. For example,
   2017-09-15T13:45:30.)
 - A batch of log events in a single request cannot span more than 24 hours. Otherwise, the operation fails.
 - Each log event can be no larger than 256 KB.
 - The maximum number of log events in a batch is 10,000.
"""
import dataclasses as dc
import json
import typing as ta

from omlish.lite.check import check

from .auth import AwsSigner
from .auth import V4AwsSigner
from .dataclasses import AwsDataclass


##


@dc.dataclass(frozen=True)
class AwsLogEvent(AwsDataclass):
    message: str
    timestamp: int  # milliseconds UTC


@dc.dataclass(frozen=True)
class AwsPutLogEventsRequest(AwsDataclass):
    log_group_name: str
    log_stream_name: str
    log_events: ta.Sequence[AwsLogEvent]
    sequence_token: ta.Optional[str] = None


@dc.dataclass(frozen=True)
class AwsRejectedLogEventsInfo(AwsDataclass):
    expired_log_event_end_index: ta.Optional[int] = None
    too_new_log_event_start_index: ta.Optional[int] = None
    too_old_log_event_end_index: ta.Optional[int] = None


@dc.dataclass(frozen=True)
class AwsPutLogEventsResponse(AwsDataclass):
    next_sequence_token: ta.Optional[str] = None
    rejected_log_events_info: ta.Optional[AwsRejectedLogEventsInfo] = None

    raw: ta.Optional[AwsDataclass.Raw] = None


##


class AwsLogMessageBuilder:
    """
    TODO:
     - max_items
     - max_bytes - manually build body
     - flush_interval
     - split sorted chunks if span over 24h
    """

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
            credentials: ta.Optional[AwsSigner.Credentials],

            url: ta.Optional[str] = None,
            service_name: str = DEFAULT_SERVICE_NAME,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            extra_headers: ta.Optional[ta.Mapping[str, str]] = None,
    ) -> None:
        super().__init__()

        self._log_group_name = check.non_empty_str(log_group_name)
        self._log_stream_name = check.non_empty_str(log_stream_name)

        if url is None:
            url = self.DEFAULT_URL.format(region_name=region_name)
        self._url = url

        if headers is None:
            headers = self.DEFAULT_HEADERS
        if extra_headers is not None:
            headers = {**headers, **extra_headers}
        self._headers = {k: [v] for k, v in headers.items()}

        signer: ta.Optional[V4AwsSigner]
        if credentials is not None:
            signer = V4AwsSigner(
                credentials,
                region_name,
                service_name,
            )
        else:
            signer = None
        self._signer = signer

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
                for m in sorted(messages, key=lambda m: m.ts_ms)
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

        if (signer := self._signer) is not None:
            sig_headers = signer.sign(
                sig_req,
                sign_payload=False,
            )
            sig_req = dc.replace(sig_req, headers={**sig_req.headers, **sig_headers})

        post = AwsLogMessageBuilder.Post(
            url=self._url,
            headers={k: check.single(v) for k, v in sig_req.headers.items()},
            data=sig_req.payload,
        )

        return [post]
