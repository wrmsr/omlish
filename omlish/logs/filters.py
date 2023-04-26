import logging
import threading


class TidFilter(logging.Filter):

    def filter(self, record):
        record.tid = threading.get_native_id()
        return True
