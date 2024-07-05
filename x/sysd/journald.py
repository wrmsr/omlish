import ctypes as ct

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


def _main():
    lib = ct.CDLL('libsystemd.so.0')

    lib.sd_journal_sendv = lib['sd_journal_sendv']
    lib.sd_journal_sendv.restype = ct.c_int
    lib.sd_journal_sendv.argtypes = [ct.POINTER(libc.iovec), ct.c_int]

    items = {
        'foo': 'bar',
        'baz': 'qux',
    }

    msgs = [('%s=%s\0' % (k.upper(), v)).encode() for k, v in items.items()]

    vec = (libc.iovec * len(msgs))()
    cl = (ct.c_char_p * len(msgs))()  # noqa
    for i in range(len(msgs)):
        vec[i].iov_base = ct.cast(ct.c_char_p(msgs[i]), ct.c_void_p)
        vec[i].iov_len = len(msgs[i]) - 1

    print(lib.sd_journal_sendv(vec, len(msgs)))


if __name__ == '__main__':
    _main()
