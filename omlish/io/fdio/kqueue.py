# ruff: noqa: UP006 UP007
import errno
import select
import sys
import typing as ta

from .pollers import FdioPoller


KqueueFdioPoller: ta.Optional[ta.Type[FdioPoller]]
if sys.platform == 'darwin' or sys.platform.startswith('freebsd'):

    class _KqueueFdioPoller(FdioPoller):
        DEFAULT_MAX_EVENTS = 1000

        def __init__(
                self,
                *,
                max_events: int = DEFAULT_MAX_EVENTS,
        ) -> None:
            super().__init__()

            self._max_events = max_events

            self._kqueue: ta.Optional[ta.Any] = None

        #

        def _get_kqueue(self) -> 'select.kqueue':
            if (kq := self._kqueue) is not None:
                return kq
            kq = select.kqueue()
            self._kqueue = kq
            return kq

        def close(self) -> None:
            if self._kqueue is not None:
                self._kqueue.close()
                self._kqueue = None

        def reopen(self) -> None:
            for fd in self._readable:
                self._register_readable(fd)
            for fd in self._writable:
                self._register_writable(fd)

        #

        def _register_readable(self, fd: int) -> None:
            self._update_registration(fd, 'read', 'add')

        def _register_writable(self, fd: int) -> None:
            self._update_registration(fd, 'write', 'add')

        def _unregister_readable(self, fd: int) -> None:
            self._update_registration(fd, 'read', 'del')

        def _unregister_writable(self, fd: int) -> None:
            self._update_registration(fd, 'write', 'del')

        #

        _CONTROL_FILTER_BY_READ_OR_WRITE: ta.ClassVar[ta.Mapping[ta.Literal['read', 'write'], int]] = {
            'read': select.KQ_FILTER_READ,
            'write': select.KQ_FILTER_WRITE,
        }

        _CONTROL_FLAGS_BY_ADD_OR_DEL: ta.ClassVar[ta.Mapping[ta.Literal['add', 'del'], int]] = {
            'add': select.KQ_EV_ADD,
            'del': select.KQ_EV_DELETE,
        }

        def _update_registration(
                self,
                fd: int,
                read_or_write: ta.Literal['read', 'write'],
                add_or_del: ta.Literal['add', 'del'],
        ) -> None:  # noqa
            ke = select.kevent(
                fd,
                filter=self._CONTROL_FILTER_BY_READ_OR_WRITE[read_or_write],
                flags=self._CONTROL_FLAGS_BY_ADD_OR_DEL[add_or_del],
            )
            kq = self._get_kqueue()
            try:
                kq.control([ke], 0)

            except OSError as exc:
                if exc.errno == errno.EBADF:
                    # log.debug('EBADF encountered in kqueue. Invalid file descriptor %s', ke.ident)
                    pass
                elif exc.errno == errno.ENOENT:
                    # Can happen when trying to remove an already closed socket
                    if add_or_del == 'add':
                        raise
                else:
                    raise

        #

        def poll(self, timeout: ta.Optional[float]) -> FdioPoller.PollResult:
            kq = self._get_kqueue()
            try:
                kes = kq.control(None, self._max_events, timeout)

            except OSError as exc:
                if exc.errno == errno.EINTR:
                    return FdioPoller.PollResult(msg='EINTR encountered in poll', exc=exc)
                else:
                    raise

            r: ta.List[int] = []
            w: ta.List[int] = []
            for ke in kes:
                if ke.filter == select.KQ_FILTER_READ:
                    r.append(ke.ident)
                if ke.filter == select.KQ_FILTER_WRITE:
                    w.append(ke.ident)

            return FdioPoller.PollResult(r, w)

    KqueueFdioPoller = _KqueueFdioPoller
else:
    KqueueFdioPoller = None
