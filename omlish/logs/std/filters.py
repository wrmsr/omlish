# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import logging
import threading


##


class TidLoggingFilter(logging.Filter):
    def filter(self, record):
        # FIXME: handle better - missing from wasm and cosmos
        if hasattr(threading, 'get_native_id'):
            record.tid = threading.get_native_id()
        else:
            record.tid = '?'
        return True
