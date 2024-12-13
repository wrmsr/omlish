# ruff: noqa: UP006 UP007
# @omlish-lite
import logging
import typing as ta


class ListHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: ta.List[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)
