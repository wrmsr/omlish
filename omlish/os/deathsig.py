# @omlish-lite
import ctypes as ct
import sys


LINUX_PR_SET_PDEATHSIG = 1  # Second arg is a signal
LINUX_PR_GET_PDEATHSIG = 2  # Second arg is a ptr to return the signal


def set_process_deathsig(sig: int) -> bool:
    if sys.platform == 'linux':
        libc = ct.CDLL('libc.so.6')

        # int prctl(int option, unsigned long arg2, unsigned long arg3, unsigned long arg4, unsigned long arg5);
        libc.prctl.restype = ct.c_int
        libc.prctl.argtypes = [ct.c_int, ct.c_ulong, ct.c_ulong, ct.c_ulong, ct.c_ulong]

        libc.prctl(LINUX_PR_SET_PDEATHSIG, sig, 0, 0, 0, 0)

        return True

    else:
        return False
