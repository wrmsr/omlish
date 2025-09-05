# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import json
import typing as ta

from omlish.io.buffers import DelimitingBuffer
from omlish.lite.check import check
from omlish.logs.modules import get_module_logger


log = get_module_logger(globals())  # noqa


##


@dc.dataclass(frozen=True)
class JournalctlMessage:
    raw: bytes
    dct: ta.Optional[ta.Mapping[str, ta.Any]] = None
    cursor: ta.Optional[str] = None
    ts_us: ta.Optional[int] = None  # microseconds UTC


class JournalctlMessageBuilder:
    def __init__(self) -> None:
        super().__init__()

        self._buf = DelimitingBuffer(b'\n')

    _cursor_field = '__CURSOR'

    _timestamp_fields: ta.Sequence[str] = [
        '_SOURCE_REALTIME_TIMESTAMP',
        '__REALTIME_TIMESTAMP',
    ]

    def _get_message_timestamp(self, dct: ta.Mapping[str, ta.Any]) -> ta.Optional[int]:
        for fld in self._timestamp_fields:
            if (tsv := dct.get(fld)) is None:
                continue

            if isinstance(tsv, str):
                try:
                    return int(tsv)
                except ValueError:
                    try:
                        return int(float(tsv))
                    except ValueError:
                        log.exception('Failed to parse timestamp: %r', tsv)

            elif isinstance(tsv, (int, float)):
                return int(tsv)

        log.error('Invalid timestamp: %r', dct)
        return None

    def _make_message(self, raw: bytes) -> JournalctlMessage:
        dct = None
        cursor = None
        ts = None

        try:
            dct = json.loads(raw.decode('utf-8', 'replace'))
        except Exception:  # noqa
            log.exception('Failed to parse raw message: %r', raw)

        else:
            cursor = dct.get(self._cursor_field)
            ts = self._get_message_timestamp(dct)

        return JournalctlMessage(
            raw=raw,
            dct=dct,
            cursor=cursor,
            ts_us=ts,
        )

    def feed(self, data: bytes) -> ta.Sequence[JournalctlMessage]:
        ret: ta.List[JournalctlMessage] = []
        for line in self._buf.feed(data):
            ret.append(self._make_message(check.isinstance(line, bytes)))
        return ret
