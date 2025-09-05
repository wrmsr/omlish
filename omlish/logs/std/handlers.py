# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import logging
import typing as ta


##


class ListLoggingHandler(logging.Handler):
    def __init__(self, record_list: ta.Optional[ta.List[logging.LogRecord]] = None) -> None:
        super().__init__()

        if record_list is None:
            record_list = []
        self.records: ta.List[logging.LogRecord] = record_list

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)
