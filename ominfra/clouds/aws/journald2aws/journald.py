# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import json
import typing as ta

from omlish.lite.check import check_isinstance
from omlish.lite.io import DelimitingBuffer
from omlish.lite.logs import log


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
    _timestamp_field = '_SOURCE_REALTIME_TIMESTAMP'

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

            if tsv := dct.get(self._timestamp_field):
                if isinstance(tsv, str):
                    try:
                        ts = int(tsv)
                    except ValueError:
                        try:
                            ts = int(float(tsv))
                        except ValueError:
                            log.exception('Failed to parse timestamp: %r', tsv)
                elif isinstance(tsv, (int, float)):
                    ts = int(tsv)
                else:
                    log.exception('Invalid timestamp: %r', tsv)

        return JournalctlMessage(
            raw=raw,
            dct=dct,
            cursor=cursor,
            ts_us=ts,
        )

    def feed(self, data: bytes) -> ta.Sequence[JournalctlMessage]:
        ret: ta.List[JournalctlMessage] = []
        for line in self._buf.feed(data):
            ret.append(self._make_message(check_isinstance(line, bytes)))  # type: ignore
        return ret
