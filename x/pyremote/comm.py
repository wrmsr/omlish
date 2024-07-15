import errno
import logging
import select
import sys
import threading
import typing as ta


log = logging.getLogger(__name__)


##


def _callbacks(obj: ta.Any, name: str) -> ta.List[ta.Callable]:
    return obj.__dict__.setdefault('_callbacks', {}).setdefault(name, [])


def callback_add(obj: ta.Any, name: str, fn) -> None:
    _callbacks(obj, name).append(fn)


def callback_remove(obj: ta.Any, name: str, fn: ta.Callable) -> None:
    _callbacks(obj, name).remove(fn)


def callback(obj: ta.Any, name: str, *args: ta.Any, **kwargs: ta.Any) -> None:
    for fn in _callbacks(obj, name):
        fn(*args, **kwargs)


##


def io_op(func, *args):
    while True:
        try:
            return func(*args), None
        except (select.error, OSError, IOError):
            e = sys.exc_info()[1]
            log.debug('io_op(%r) -> OSError: %s', func, e)
            if e.args[0] == errno.EINTR:
                continue
            if e.args[0] in (errno.EIO, errno.ECONNRESET, errno.EPIPE):
                return None, e
            raise


##


class Poller:

    class Entry(ta.NamedTuple):
        data: ta.Any
        gen: int

    def __init__(self) -> None:
        super().__init__()
        self._rfds: ta.Dict[int, Poller.Entry] = {}
        self._wfds: ta.Dict[int, Poller.Entry] = {}
        self._gen = 1

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}'

    @property
    def readers(self) -> ta.List[ta.Tuple[ta.Any, int]]:
        return list((fd, data) for fd, (data, gen) in self._rfds.items())

    @property
    def writers(self) -> ta.List[ta.Tuple[ta.Any, int]]:
        return list((fd, data) for fd, (data, gen) in self._wfds.items())

    def start_receive(self, fd: int, data: ta.Any = None) -> None:
        self._rfds[fd] = Poller.Entry(data or fd, self._gen)

    def stop_receive(self, fd: int) -> None:
        self._rfds.pop(fd, None)

    def start_transmit(self, fd: int, data: ta.Any = None) -> None:
        self._wfds[fd] = Poller.Entry(data or fd, self._gen)

    def stop_transmit(self, fd: int) -> None:
        self._wfds.pop(fd, None)

    def _poll(self, timeout: ta.Optional[float]) -> ta.Iterable[ta.Any]:
        (rfds, wfds, _), _ = io_op(
            select.select,
            self._rfds,
            self._wfds,
            (),
            timeout,
        )

        for fd in rfds:
            log.debug('%r: read for %r', self, fd)
            e = self._rfds.get(fd, (None, None))
            if e.gen and e.gen < self._gen:
                yield e.data

        for fd in wfds:
            log.debug('%r: write for %r', self, fd)
            e = self._wfds.get(fd, (None, None))
            if e.gen and e.gen < self._gen:
                yield e.data

    def poll(self, timeout: ta.Optional[float] = None) -> ta.Iterable[ta.Any]:
        log.debug('%r: poll(%r)', self, timeout)
        self._gen += 1
        return self._poll(timeout)


class Broker:

    def __init__(self) -> None:
        super().__init__()

        self._alive = True
        self._exited = False

        self._poller = Poller()

        self._thread = threading.Thread(
            target=self._broker_main,
            name=f'{repr(self)}._broker_main',
        )
        self._thread.start()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}'

    def _loop_once(self, timeout: ta.Optional[float] = None) -> None:
        timer_to = self.timers.get_timeout()
        if timeout is None:
            timeout = timer_to
        elif timer_to is not None and timer_to < timeout:
            timeout = timer_to

        for side, func in self.poller.poll(timeout):
            self._call(side.stream, func)
        if timer_to is not None:
            self.timers.expire()

    def _broker_exit(self):
        for _, (side, _) in self.poller.readers + self.poller.writers:
            log.debug('%r: force disconnecting %r', self, side)
            side.stream.on_disconnect(self)

        self.poller.close()

    def _broker_shutdown(self):
        for _, (side, _) in self.poller.readers + self.poller.writers:
            self._call(side.stream, side.stream.on_shutdown)

        deadline = now() + self.shutdown_timeout
        while self.keep_alive() and now() < deadline:
            self._loop_once(max(0, deadline - now()))

        if self.keep_alive():
            log.error(
                '%r: pending work still existed %d seconds after shutdown began. This may be due to a timer that is '
                'yet to expire, or a child connection that did not fully shut down.',
                self,
                self.shutdown_timeout,
            )

    def _do_broker_main(self) -> None:
        try:
            while self._alive:
                self._loop_once()

            callback(self, 'before_shutdown')
            callback(self, 'shutdown')
            self._broker_shutdown()
        except Exception:  # noqa
            log.exception('%r: broker crashed', self)

        self._alive = False  # Ensure _alive is consistent on crash.
        self._exited = True
        self._broker_exit()

    def _broker_main(self) -> None:
        try:
            self._do_broker_main()
        finally:
            # 'finally' to ensure _on_broker_exit() can always SIGTERM.
            callback(self, 'exit')

    def shutdown(self) -> None:
        _v and LOG.debug('%r: shutting down', self)
        def _shutdown():
            self._alive = False
        if self._alive and not self._exited:
            self.defer(_shutdown)

    def join(self) -> None:
        self._thread.join()


def _main() -> None:
    pass


if __name__ == '__main__':
    _main()
