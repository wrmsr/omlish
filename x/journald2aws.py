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
import time
import typing as ta

import httpx

from omdev.secrets import load_secrets
from ominfra.clouds.aws.auth import V4AwsSigner
from omlish.formats import json
from omlish.lite.strings import camel_case


##


class AwsDataclass:
    _aws_field_maps: ta.ClassVar[ta.Optional[ta.Tuple[
        ta.Mapping[str, str],  # dc -> aws
        ta.Mapping[str, str],  # aws -> dc
    ]]] = None

    @classmethod
    def _get_aws_field_maps(cls) -> ta.Tuple[ta.Mapping[str, str], ta.Mapping[str, str]]:
        try:
            return cls.__dict__['_aws_field_maps']
        except KeyError:
            pass

        d2a, a2d = {}, {}
        for f in dc.fields(cls):  # noqa
            d = f.name
            a = camel_case(d, lower=True)
            d2a[d] = a
            a2d[a] = d

        ret = cls._aws_field_maps = (d2a, a2d)
        return ret


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


print(AwsLogEvent._get_aws_field_maps())
print(AwsPutLogEventsResponse._get_aws_field_maps())


def _main() -> None:
    secrets = load_secrets()

    payload = {
        "logGroupName": "omlish",
        "logStreamName": "test",
        "logEvents": [
            {"timestamp": int(time.time() * 1000.), "message": "Test log message 3"},
        ],
    }
    body = json.dumps_compact(payload).encode('utf-8')

    amz_target = 'Logs_20140328.PutLogEvents'
    url = 'https://logs.us-west-1.amazonaws.com/'

    creds = V4AwsSigner.Credentials(
        secrets.get('aws_access_key_id').reveal(),
        secrets.get('aws_secret_access_key').reveal(),

    )

    region_name = 'us-west-1'

    #

    req = V4AwsSigner.Request(
        method='POST',
        url=url,
        headers={
            'User-Agent': ['Botocore/1.35.6 ua/2.0 os/macos#21.6.0 md/arch#arm64 lang/python#3.12.5 md/pyimpl#CPython'],
            'Content-Type': ['application/x-amz-json-1.1'],
            'X-Amz-Target': [amz_target],
        },
        payload=body,
    )

    #

    sign_hdrs = V4AwsSigner(creds, region_name, 'logs').sign(req, sign_payload=False)
    req = dc.replace(req, headers={**req.headers, **sign_hdrs})

    resp = httpx.post(
        req.url,
        headers=[(k, v) for k, vs in req.headers.items() for v in vs],
        follow_redirects=True,
        content=req.payload,
    )

    print((resp, resp.content))


if __name__ == '__main__':
    _main()
