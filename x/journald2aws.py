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
import operator
import time
import typing as ta

import httpx

from omdev.secrets import load_secrets
from ominfra.clouds.aws.auth import V4AwsSigner
from omlish.formats import json
from omlish.lite.strings import camel_case


##


class AwsDataclass:
    class _AwsField(ta.NamedTuple):
        d: str
        a: str

    _aws_fields: ta.ClassVar[ta.Sequence[_AwsField]] = None

    @classmethod
    def _get_aws_fields(cls) -> ta.Sequence[_AwsField]:
        try:
            return cls.__dict__['_aws_fields']
        except KeyError:
            pass

        fs = []
        for f in dc.fields(cls):  # noqa
            d = f.name
            a = camel_case(d, lower=True)
            fs.append(AwsDataclass._AwsField(d, a))

        cls._aws_fields = fs
        return fs

    #

    class _AwsConverters(ta.NamedTuple):
        d2a: ta.Callable
        a2d: ta.Callable

    _aws_converters: ta.ClassVar[ta.Optional[_AwsConverters]] = None

    @classmethod
    def _get_aws_converters(cls) -> _AwsConverters:
        try:
            return cls.__dict__['_aws_converters']
        except KeyError:
            pass

        fs = cls._get_aws_fields()

        def d2a(o):
            dct = {}
            for f in fs:
                x = getattr(o, f.d)
                if x is not None:
                    dct[f.a] = x
            return dct

        def a2d(v):
            dct = {}
            for f in fs:
                x = v.get(f.a)
                if x is not None:
                    dct[f.d] = x
            return cls(**dct)

        ret = cls._aws_converters = AwsDataclass._AwsConverters(d2a, a2d)
        return ret

    def to_aws(self) -> ta.Mapping[str, ta.Any]:
        return self._get_aws_converters().d2a(self)

    @classmethod
    def from_aws(cls, v: ta.Mapping[str, ta.Any]) -> 'AwsDataclass':
        return cls._get_aws_converters().a2d(v)


@dc.dataclass(frozen=True)
class AwsLogEvent(AwsDataclass):
    message: str
    timestamp: int


@dc.dataclass(frozen=True)
class AwsPutLogEventsRequest(AwsDataclass):
    log_group_name: str
    log_stream_name: str
    log_events: ta.List[AwsLogEvent]
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

    raw: ta.Any = None


##


def _main() -> None:
    secrets = load_secrets()

    payload = {
        "logGroupName": "omlish",
        "logStreamName": "test",
        "logEvents": [
            {"timestamp": int(time.time() * 1000.), "message": "Test log message 3"},
        ],
    }

    print(AwsPutLogEventsRequest.from_aws(payload))

    # body = json.dumps_compact(payload).encode('utf-8')
    #
    # amz_target = 'Logs_20140328.PutLogEvents'
    # url = 'https://logs.us-west-1.amazonaws.com/'
    #
    # creds = V4AwsSigner.Credentials(
    #     secrets.get('aws_access_key_id').reveal(),
    #     secrets.get('aws_secret_access_key').reveal(),
    #
    # )
    #
    # region_name = 'us-west-1'
    #
    # #
    #
    # req = V4AwsSigner.Request(
    #     method='POST',
    #     url=url,
    #     headers={
    #         'User-Agent': ['Botocore/1.35.6 ua/2.0 os/macos#21.6.0 md/arch#arm64 lang/python#3.12.5 md/pyimpl#CPython'],
    #         'Content-Type': ['application/x-amz-json-1.1'],
    #         'X-Amz-Target': [amz_target],
    #     },
    #     payload=body,
    # )
    #
    # #
    #
    # sign_hdrs = V4AwsSigner(creds, region_name, 'logs').sign(req, sign_payload=False)
    # req = dc.replace(req, headers={**req.headers, **sign_hdrs})
    #
    # resp = httpx.post(
    #     req.url,
    #     headers=[(k, v) for k, vs in req.headers.items() for v in vs],
    #     follow_redirects=True,
    #     content=req.payload,
    # )
    #
    # print((resp, resp.content))


if __name__ == '__main__':
    _main()
