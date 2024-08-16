import abc
import dataclasses as dc
import typing as ta


##


class Event(abc.ABC):
    pass


class IllegalStateException(Exception):
    pass


##


@dc.dataclass(frozen=True)
class RecvdData(Event):
    data: bytes


class LineReader:
    def __init__(self) -> None:
        super().__init__()
        self._buf = bytearray()

    def accept(self, e: Event) -> ta.Iterable[Event]:
        if isinstance(e, RecvdData):
            self._buf += e.data
            out = []
            while (i := self._buf.find(b'\n')) >= 0:
                out.append(RecvdLine(self._buf[:i+1].decode()))
                self._buf = self._buf[i+1:]
            return out
        raise IllegalStateException


##


@dc.dataclass(frozen=True)
class RecvdLine(Event):
    line: str


@dc.dataclass(frozen=True)
class SendLine(Event):
    line: str


##


class AckedEchoProtocol(abc.ABC):
    ACK0 = 'hi0\n'
    ACK1 = 'hi1\n'


class AckedEchoProtocol0(AckedEchoProtocol):
    def __init__(self) -> None:
        super().__init__()
        self._state = 0

    def accept(self, e: Event) -> ta.Iterable[Event]:
        if self._state == 0:
            if isinstance(e, RecvdLine):
                if e.line == self.ACK0:
                    self._state = 1
                    return []
        if self._state == 1:
            if isinstance(e, RecvdLine):
                if e.line == self.ACK1:
                    self._state = 2
                    return []
        if self._state == 2:
            if isinstance(e, RecvdLine):
                return [SendLine(e.line)]
        raise IllegalStateException


##


def _main() -> None:
    for oe in LineReader().accept(RecvdData(b'hi\nthere\n')):
        print(repr(oe))

    def handle_output(e: Event) -> None:
        if isinstance(e, SendLine):
            print(repr(e))
            return
        raise IllegalStateException

    p = AckedEchoProtocol0()

    for ie in [
        RecvdLine('hi0\n'),
        RecvdLine('hi1\n'),
        RecvdLine('foo\n'),
        RecvdLine('bar\n'),
    ]:
        for oe in p.accept(ie):
            handle_output(oe)


if __name__ == '__main__':
    _main()
