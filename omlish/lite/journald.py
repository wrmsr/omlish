# ruff: noqa: UP012
import ctypes as ct
import typing as ta

from .cached import cached_nullary


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
    try:
        lib = ct.CDLL('libsystemd.so.0')
    except OSError:  # noqa
        raise

    lib.sd_journal_sendv = lib['sd_journal_sendv']  # type: ignore
    lib.sd_journal_sendv.restype = ct.c_int
    lib.sd_journal_sendv.argtypes = [ct.POINTER(sd_iovec), ct.c_int]

    return lib


##


def sd_journald_send(**kwargs: str) -> int:
    lib = sd_libsystemd()

    msgs = [
        f'{k.upper()}={v}\0'.encode('utf-8')
        for k, v in kwargs.items()
    ]

    vec = (sd_iovec * len(msgs))()
    cl = (ct.c_char_p * len(msgs))()  # noqa
    for i in range(len(msgs)):
        vec[i].iov_base = ct.cast(ct.c_char_p(msgs[i]), ct.c_void_p)
        vec[i].iov_len = len(msgs[i]) - 1

    return lib.sd_journal_sendv(vec, len(msgs))
