import abc
import dataclasses as dc
import typing as ta

from .events import Event
from .events import WaitableEvent
from .events import Waitables
from .core import DelegationEvent
from .core import ReturnEvent


##


class FileEvent(Event, abc.ABC):
    pass


##


@dc.dataclass(frozen=True, eq=False)
class ReadEvent(WaitableEvent, FileEvent):
    """Reads from a file-like object."""

    fd: ta.IO
    bufsize: int

    def waitables(self) -> Waitables:
        return Waitables(r=[self.fd])

    def fire(self) -> bytes:
        return self.fd.read(self.bufsize)


def read(fd: ta.IO, bufsize: int | None = None) -> Event:
    """Event: read from a file descriptor asynchronously."""

    if bufsize is None:
        # Read all.
        def reader():
            buf = []
            while True:
                data = yield read(fd, 1024)
                if not data:
                    break
                buf.append(data)
            yield ReturnEvent(''.join(buf))

        return DelegationEvent(reader())

    else:
        return ReadEvent(fd, bufsize)


##


@dc.dataclass(frozen=True, eq=False)
class WriteEvent(WaitableEvent, FileEvent):
    """Writes to a file-like object."""

    fd: ta.IO
    data: bytes

    def waitables(self) -> Waitables:
        return Waitables(w=[self.fd])

    def fire(self) -> None:
        self.fd.write(self.data)


def write(fd: ta.IO, data: bytes) -> Event:
    """Event: write to a file descriptor asynchronously."""

    return WriteEvent(fd, data)
