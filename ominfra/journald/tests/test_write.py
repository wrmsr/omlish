"""
- https://www.freedesktop.org/software/systemd/man/latest/systemd.journal-fields.html
- https://github.com/mosquito/cysystemd/tree/master/cysystemd

priorities
LOG_EMERG   = 0   /* system is unusable */
LOG_ALERT   = 1   /* action must be taken immediately */
LOG_CRIT    = 2   /* critical conditions */
LOG_ERR     = 3   /* error conditions */
LOG_WARNING = 4   /* warning conditions */
LOG_NOTICE  = 5   /* normal but significant condition */
LOG_INFO    = 6   /* informational */
LOG_DEBUG   = 7   /* debug-level messages */

facilities
LOG_KERN     = 0  /* kernel messages */
LOG_USER     = 1  /* random user-level messages */
LOG_MAIL     = 2  /* mail system */
LOG_DAEMON   = 3  /* system daemons */
LOG_AUTH     = 4  /* security/authorization messages */
LOG_SYSLOG   = 5  /* messages generated internally by syslogd */
LOG_LPR      = 6  /* line printer subsystem */
LOG_NEWS     = 7  /* network news subsystem */
LOG_UUCP     = 8  /* UUCP subsystem */
LOG_CRON     = 9  /* clock daemon */
LOG_AUTHPRIV = 10 /* security/authorization messages (private) */
LOG_FTP      = 11 /* ftp daemon */

LOG_LOCAL0   = 16 /* reserved for local use */
LOG_LOCAL1   = 17 /* reserved for local use */
LOG_LOCAL2   = 18 /* reserved for local use */
LOG_LOCAL3   = 19 /* reserved for local use */
LOG_LOCAL4   = 20 /* reserved for local use */
LOG_LOCAL5   = 21 /* reserved for local use */
LOG_LOCAL6   = 22 /* reserved for local use */
LOG_LOCAL7   = 23 /* reserved for local use */

LOG_PID     = 0x01    /* log the pid with each message */
LOG_CONS    = 0x02    /* log on the console if errors in sending */
LOG_ODELAY  = 0x04    /* delay open until first syslog() (default) */
LOG_NDELAY  = 0x08    /* don't delay open */
LOG_NOWAIT  = 0x10    /* don't wait for console forks: DEPRECATED */
LOG_PERROR  = 0x20    /* log to stderr as well */

https://www.freedesktop.org/software/systemd/man/latest/systemd.journal-fields.html

ts = current_time_micros

hash_fields = (
    message,
    record.funcName,
    record.levelno,
    record.process,
    record.processName,
    record.levelname,
    record.pathname,
    record.name,
    record.thread,
    record.lineno,
    ts,
    tb_message,
)

message_id = uuid.uuid3(uuid.NAMESPACE_OID, "$".join(str(x) for x in hash_fields)).hex

message
priority
syslog_facility
code_file
code_line
code_func
syslog_identifier
message_raw
message_id
code_module
logger_name
pid
proccess_name
errno
relative_ts
thread_name
"""
import ctypes as ct

import pytest

from omlish import libc


SD_JOURNAL_LOCAL_ONLY = 1 << 0
SD_JOURNAL_RUNTIME_ONLY = 1 << 1
SD_JOURNAL_SYSTEM = 1 << 2
SD_JOURNAL_CURRENT_USER = 1 << 3
SD_JOURNAL_OS_ROOT = 1 << 4
SD_JOURNAL_ALL_NAMESPACES = 1 << 5
SD_JOURNAL_INCLUDE_DEFAULT_NAMESPACE = 1 << 6

SD_JOURNAL_NOP = 0
SD_JOURNAL_APPEND = 1
SD_JOURNAL_INVALIDATE = 2


def test_write():
    try:
        lib = ct.CDLL('libsystemd.so.0')
    except OSError:
        pytest.skip('Failed to find libsystemd')

    lib.sd_journal_sendv = lib['sd_journal_sendv']  # type: ignore
    lib.sd_journal_sendv.restype = ct.c_int
    lib.sd_journal_sendv.argtypes = [ct.POINTER(libc.iovec), ct.c_int]

    items = {
        'message': 'hi',
        'priority': 'info',
        'foo': 'bar',
        'baz': 'qux',
    }

    msgs = [('%s=%s\0' % (k.upper(), v)).encode() for k, v in items.items()]  # noqa

    vec = (libc.iovec * len(msgs))()
    cl = (ct.c_char_p * len(msgs))()  # noqa
    for i in range(len(msgs)):
        vec[i].iov_base = ct.cast(ct.c_char_p(msgs[i]), ct.c_void_p)
        vec[i].iov_len = len(msgs[i]) - 1

    print(lib.sd_journal_sendv(vec, len(msgs)))
