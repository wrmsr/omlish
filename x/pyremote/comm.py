import errno
import select
import sys
import typing as ta


def io_op(func, *args):
    while True:
        try:
            return func(*args), None
        except (select.error, OSError, IOError):
            e = sys.exc_info()[1]
            if e.args[0] == errno.EINTR:
                continue
            if e.args[0] in (errno.EIO, errno.ECONNRESET, errno.EPIPE):
                return None, e
            raise


class Poller:

    class Entry(ta.NamedTuple):
        data: ta.Any
        gen: int

    def __init__(self) -> None:
        super().__init__()
        self._rfds: ta.Dict[int, Poller.Entry] = {}
        self._wfds: ta.Dict[int, Poller.Entry] = {}
        self._gen = 1

    def __repr__(self):
        return '%s' % (type(self).__name__,)

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
            e = self._rfds.get(fd, (None, None))
            if e.gen and e.gen < self._gen:
                yield e.data

        for fd in wfds:
            e = self._wfds.get(fd, (None, None))
            if e.gen and e.gen < self._gen:
                yield e.data

    def poll(self, timeout: ta.Optional[float] = None) -> ta.Iterable[ta.Any]:
        self._gen += 1
        return self._poll(timeout)


class Broker:
    pass
