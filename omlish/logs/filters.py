# ruff: noqa: UP006 UP007
# @omlish-lite
import logging
import threading


##


class TidLogFilter(logging.Filter):
    def filter(self, record):
        # FIXME: handle better - missing from wasm and cosmos
        if hasattr(threading, 'get_native_id'):
            record.tid = threading.get_native_id()
        else:
            record.tid = '?'
        return True
