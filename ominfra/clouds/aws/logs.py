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
import typing as ta

from .dataclasses import AwsDataclass


@dc.dataclass(frozen=True)
class AwsLogEvent(AwsDataclass):
    message: str
    timestamp: int


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
