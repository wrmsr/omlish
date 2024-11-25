if sys.platform == 'darwin' or sys.platform.startswith('freebsd'):
    class KqueueFdIoPoller(FdIoPoller):
        max_events = 1000

        def __init__(self) -> None:
            super().__init__()

            self._kqueue: ta.Optional[ta.Any] = select.kqueue()

        #

        def register_readable(self, fd: Fd) -> None:
            super().register_readable(fd)
            kevent = select.kevent(fd, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_ADD)
            self._kqueue_control(fd, kevent)

        def register_writable(self, fd: Fd) -> None:
            super().register_writable(fd)
            kevent = select.kevent(fd, filter=select.KQ_FILTER_WRITE, flags=select.KQ_EV_ADD)
            self._kqueue_control(fd, kevent)

        def unregister_readable(self, fd: Fd) -> None:
            kevent = select.kevent(fd, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_DELETE)
            super().unregister_readable(fd)
            self._kqueue_control(fd, kevent)

        def unregister_writable(self, fd: Fd) -> None:
            kevent = select.kevent(fd, filter=select.KQ_FILTER_WRITE, flags=select.KQ_EV_DELETE)
            super().unregister_writable(fd)
            self._kqueue_control(fd, kevent)

        #

        def close(self) -> None:
            self._kqueue.close()  # type: ignore
            self._kqueue = None

        #

        def poll(self, timeout: ta.Optional[float]) -> Poller.PollResult:
            readable, writable = [], []  # type: ignore

            try:
                kevents = self._kqueue.control(None, self.max_events, timeout)  # type: ignore
            except OSError as error:
                if error.errno == errno.EINTR:
                    log.debug('EINTR encountered in poll')
                    return Poller.PollResult(readable, writable)
                raise

            for kevent in kevents:
                if kevent.filter == select.KQ_FILTER_READ:
                    readable.append(kevent.ident)
                if kevent.filter == select.KQ_FILTER_WRITE:
                    writable.append(kevent.ident)

            return Poller.PollResult(readable, writable)

        def _kqueue_control(self, fd: Fd, kevent: 'select.kevent') -> None:
            try:
                self._kqueue.control([kevent], 0)  # type: ignore
            except OSError as error:
                if error.errno == errno.EBADF:
                    log.debug('EBADF encountered in kqueue. Invalid file descriptor %s', fd)
                else:
                    raise

        #

        def before_daemonize(self) -> None:
            self.close()

        def after_daemonize(self) -> None:
            self._kqueue = select.kqueue()
            for fd in self._readable:
                self.register_readable(fd)
            for fd in self._writable:
                self.register_writable(fd)

else:
    KqueuePoller = None
