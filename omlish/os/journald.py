# ruff: noqa: UP007 UP012
# @omlish-lite
import ctypes as ct
import logging
import sys
import syslog
import threading
import typing as ta

from ..lite.cached import cached_nullary


##


class sd_iovec(ct.Structure):  # noqa
    pass


sd_iovec._fields_ = [
    ('iov_base', ct.c_void_p),  # Pointer to data.
    ('iov_len', ct.c_size_t),  # Length of data.
]


##


@cached_nullary
def sd_libsystemd() -> ta.Any:
    lib = ct.CDLL('libsystemd.so.0')

    lib.sd_journal_sendv.restype = ct.c_int
    lib.sd_journal_sendv.argtypes = [ct.POINTER(sd_iovec), ct.c_int]

    return lib


@cached_nullary
def sd_try_libsystemd() -> ta.Optional[ta.Any]:
    try:
        return sd_libsystemd()
    except OSError:  # noqa
        return None


##


def sd_journald_send(**fields: str) -> int:
    lib = sd_libsystemd()

    msgs = [
        f'{k.upper()}={v}\0'.encode('utf-8')
        for k, v in fields.items()
    ]

    vec = (sd_iovec * len(msgs))()
    cl = (ct.c_char_p * len(msgs))()  # noqa
    for i in range(len(msgs)):
        vec[i].iov_base = ct.cast(ct.c_char_p(msgs[i]), ct.c_void_p)
        vec[i].iov_len = len(msgs[i]) - 1

    return lib.sd_journal_sendv(vec, len(msgs))


##


SD_LOG_LEVEL_MAP: ta.Mapping[int, int] = {
    logging.FATAL: syslog.LOG_EMERG,  # system is unusable
    # LOG_ALERT ?  # action must be taken immediately
    logging.CRITICAL: syslog.LOG_CRIT,
    logging.ERROR: syslog.LOG_ERR,
    logging.WARNING: syslog.LOG_WARNING,
    # LOG_NOTICE ?  # normal but significant condition
    logging.INFO: syslog.LOG_INFO,
    logging.DEBUG: syslog.LOG_DEBUG,
}


class JournaldLogHandler(logging.Handler):
    """
    TODO:
     - fallback handler for when this barfs
    """

    def __init__(
            self,
            *,
            use_formatter_output: bool = False,
    ) -> None:
        super().__init__()

        sd_libsystemd()

        self._use_formatter_output = use_formatter_output

    #

    EXTRA_RECORD_ATTRS_BY_JOURNALD_FIELD: ta.ClassVar[ta.Mapping[str, str]] = {
        'name': 'name',
        'module': 'module',
        'exception': 'exc_text',
        'thread_name': 'threadName',
        'task_name': 'taskName',
    }

    def make_fields(self, record: logging.LogRecord) -> ta.Mapping[str, str]:
        formatter_message = self.format(record)
        if self._use_formatter_output:
            message = formatter_message
        else:
            message = record.message

        fields: dict[str, str] = {
            'message': message,
            'priority': str(SD_LOG_LEVEL_MAP[record.levelno]),
            'tid': str(threading.get_ident()),
        }

        if (pathname := record.pathname) is not None:
            fields['code_file'] = pathname
        if (lineno := record.lineno) is not None:
            fields['code_lineno'] = str(lineno)
        if (func_name := record.funcName) is not None:
            fields['code_func'] = func_name

        for f, a in self.EXTRA_RECORD_ATTRS_BY_JOURNALD_FIELD.items():
            if (v := getattr(record, a, None)) is not None:
                fields[f] = str(v)

        return fields

    #

    def emit(self, record: logging.LogRecord) -> None:
        try:
            fields = self.make_fields(record)

            if rc := sd_journald_send(**fields):
                raise RuntimeError(f'{self.__class__.__name__}.emit failed: {rc=}')  # noqa

        except RecursionError:  # See issue 36272
            raise

        except Exception:  # noqa
            self.handleError(record)


def journald_log_handler_factory(
        *,
        no_tty_check: bool = False,
        no_fallback: bool = False,
) -> logging.Handler:
    if (
            sys.platform == 'linux' and
            (no_tty_check or not sys.stderr.isatty()) and
            (no_fallback or sd_try_libsystemd() is not None)
    ):
        return JournaldLogHandler()

    return logging.StreamHandler()
