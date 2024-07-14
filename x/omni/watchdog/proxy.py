import typing as ta

import wrapt

from .. import check
from .current import current


def make_suspending_proxy(methods: ta.Iterable[str]):
    check.arg(not isinstance(methods, str))

    def make_wrapper(mn):
        def wrapper(self, *args, **kwargs):
            with current().suspend_thread_current():
                return getattr(self.__wrapped__, mn)(*args, **kwargs)
        return wrapper

    ns = {}
    for mn in methods:
        ns[mn] = make_wrapper(mn)

    return type('WatchDog$SuspendingProxy', (wrapt.ObjectProxy,), ns)


SuspendingFileProxy = make_suspending_proxy({
    'flush',
    'read',
    'readinto',
    'readline',
    'readlines',
    'write',
    'writelines',
})


class SuspendingSocketProxy(make_suspending_proxy({
    'recv',
    'recv_into',
    'recvfrom',
    'recvfrom_into',
    'recvmsg',
    'recvmsg_into',
    'send',
    'sendall',
    'sendfile',
    'sendmsg',
    'sendto',
})):

    def makefile(self, *args, **kwargs):
        return SuspendingFileProxy(self.__wrapped__.makefile(*args, **kwargs))
