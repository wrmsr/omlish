# ruff: noqa: UP006 UP007
# @omlish-lite
import logging
import threading


class TidLogFilter(logging.Filter):
    def filter(self, record):
        record.tid = threading.get_native_id()
        return True
