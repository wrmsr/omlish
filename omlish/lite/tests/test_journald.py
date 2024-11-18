# ruff: noqa: PT009
"""
See:
 - https://github.com/mosquito/cysystemd/tree/master/cysystemd

==

LOG_PID     = 0x01    /* log the pid with each message */
LOG_CONS    = 0x02    /* log on the console if errors in sending */
LOG_ODELAY  = 0x04    /* delay open until first syslog() (default) */
LOG_NDELAY  = 0x08    /* don't delay open */
LOG_NOWAIT  = 0x10    /* don't wait for console forks: DEPRECATED */
LOG_PERROR  = 0x20    /* log to stderr as well */

==

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

==

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

==

{
"BAZ":"qux",
"FOO":"bar",
"MESSAGE":"hi",
"PRIORITY":"info",
"SYSLOG_IDENTIFIER":"python",
"_AUDIT_LOGINUID":"1000",
"_AUDIT_SESSION":"1",
"_BOOT_ID":"...",
"_CAP_EFFECTIVE":"0",
"_CMDLINE":"./.venvs/default/bin/python -mpytest -svv ominfra/journald/tests/test_write.py",
"_COMM":"python",
"_EXE":"/home/spinlock/.pyenv/versions/3.12.7/bin/python3.12",
"_GID":"1000",
"_HOSTNAME":"spinlock-ws",
"_MACHINE_ID":"...",
"_PID":"868213",
"_SELINUX_CONTEXT":"unconfined\n",
"_SOURCE_REALTIME_TIMESTAMP":"1731965377447341",
"_SYSTEMD_CGROUP":"/user.slice/user-1000.slice/user@1000.service/app.slice/app-org.gnome.Terminal.slice/vte-....scope",
"_SYSTEMD_INVOCATION_ID":"...",
"_SYSTEMD_SLICE":"user-1000.slice",
"_SYSTEMD_UNIT":"user@1000.service",
"_SYSTEMD_USER_SLICE":"app-org.gnome.Terminal.slice",
"_SYSTEMD_USER_UNIT":"vte-spawn-....scope",
"_TRANSPORT":"journal",
"_UID":"1000",
"__CURSOR":"...",
"__MONOTONIC_TIMESTAMP":"1400709028939",
"__REALTIME_TIMESTAMP":"1731965377447437",
_SYSTEMD_OWNER_UID":"1000"
}
"""
import unittest

from .. import journald


class TestJournald(unittest.TestCase):
    def test_write(self):
        try:
            journald.sd_libsystemd()
        except OSError:
            self.skipTest('Failed to find libsystemd')
            raise RuntimeError  # noqa

        self.assertEqual(journald.sd_journald_send(**{  # noqa
            'message': 'hi',
            'priority': 'info',
            'foo': 'bar',
            'baz': 'qux',
        }), 0)
