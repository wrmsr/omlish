import abc
import dataclasses as dc
import random
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


#


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
                return [SendLine('echo ' + e.line)]
        raise IllegalStateException


#


class AckedEchoProtocol1(AckedEchoProtocol):
    def __init__(self) -> None:
        super().__init__()
        self.accept = self._accept_0

    accept: ta.Callable[[Event], ta.Iterable[Event]]

    def _accept_0(self, e: Event) -> ta.Iterable[Event]:
        if isinstance(e, RecvdLine):
            if e.line == self.ACK0:
                self.accept = self._accept_1
                return []
        raise IllegalStateException

    def _accept_1(self, e: Event) -> ta.Iterable[Event]:
        if isinstance(e, RecvdLine):
            if e.line == self.ACK1:
                self.accept = self._accept_2
                return []
        raise IllegalStateException

    def _accept_2(self, e: Event) -> ta.Iterable[Event]:
        if isinstance(e, RecvdLine):
            return [SendLine('echo ' + e.line)]
        raise IllegalStateException


#


AckedEchoProtocol2State: ta.TypeAlias = ta.Callable[[Event], tuple['AckedEchoProtocol2State', ta.Iterable[Event]]]


class AckedEchoProtocol2(AckedEchoProtocol):

    def __init__(self) -> None:
        super().__init__()
        self._state: AckedEchoProtocol2State = self._accept_0

    def accept(self, e: Event) -> ta.Iterable[Event]:
        self._state, oe = self._state(e)
        return oe

    def _accept_0(self, e: Event) -> tuple[AckedEchoProtocol2State, ta.Iterable[Event]]:
        if isinstance(e, RecvdLine):
            if e.line == self.ACK0:
                return (self._accept_1, [])
        raise IllegalStateException

    def _accept_1(self, e: Event) -> tuple[AckedEchoProtocol2State, ta.Iterable[Event]]:
        if isinstance(e, RecvdLine):
            if e.line == self.ACK1:
                return (self._accept_2, [])
        raise IllegalStateException

    def _accept_2(self, e: Event) -> tuple[AckedEchoProtocol2State, ta.Iterable[Event]]:
        if isinstance(e, RecvdLine):
            return (self._accept_2, [SendLine('echo ' + e.line)])
        raise IllegalStateException


#


class AckedEchoProtocol3(AckedEchoProtocol):
    def __init__(self) -> None:
        super().__init__()
        self._gen = self._accept()
        if (e := next(self._gen)):  # noqa
            raise IllegalStateException

    def accept(self, e: Event) -> ta.Iterable[Event]:
        return self._gen.send(e)

    def _accept(self) -> ta.Generator[ta.Iterable[Event], Event, None]:
        out = []

        for ack in [self.ACK0, self.ACK1]:
            e = yield out
            if not isinstance(e, RecvdLine) and e.line == ack:
                raise IllegalStateException

        while True:
            e = yield out
            if isinstance(e, RecvdLine):
                out = [SendLine('echo ' + e.line)]
            else:
                raise IllegalStateException


#


class AckedEchoProtocol4(AckedEchoProtocol):
    """like 3 but some kind of thunky thing to avoid `i = yield o` awkwardness."""

    def __init__(self) -> None:
        super().__init__()
        self._gen = self._accept()
        if (e := next(self._gen)):  # noqa
            raise IllegalStateException

    def accept(self, e: Event) -> ta.Iterable[Event]:
        while (o := self._gen.send(e)) is not None:
            yield from o

    def _accept(self) -> ta.Generator[ta.Iterable[Event] | None, Event, None]:
        for ack in [self.ACK0, self.ACK1]:
            e = yield
            if not isinstance(e, RecvdLine) and e.line == ack:
                raise IllegalStateException

        while True:
            e = yield
            if isinstance(e, RecvdLine):
                yield [SendLine('echo ' + e.line)]
            else:
                raise IllegalStateException


#


EventStep: ta.TypeAlias = ta.Iterable[Event] | None
EventGenerator: ta.TypeAlias = ta.Generator[EventStep, Event, ta.Optional['EventGenerator']]


class AckedEchoProtocol5(AckedEchoProtocol):
    """like 4 but can switch acceptor gens."""

    def __init__(self) -> None:
        super().__init__()
        self._gen: EventGenerator | None = self._accept_0()
        if (n := next(self._gen)):  # noqa
            raise IllegalStateException

    def accept(self, e: Event) -> ta.Iterable[Event]:
        if self._gen is None:
            raise IllegalStateException
        try:
            while (o := self._gen.send(e)) is not None:
                yield from o
        except StopIteration as s:
            if s.value is None:
                raise IllegalStateException
            self._gen = s.value
            if (n := next(self._gen)):  # noqa
                raise IllegalStateException

    def _accept_0(self) -> EventGenerator:
        for ack in [self.ACK0, self.ACK1]:
            e = yield
            if not isinstance(e, RecvdLine) and e.line == ack:
                raise IllegalStateException
        return self._accept_1()

    def _accept_1(self) -> EventGenerator:
        while True:
            e = yield
            if isinstance(e, RecvdLine):
                yield [SendLine('echo ' + e.line)]
            else:
                raise IllegalStateException


#


class AckedEchoProtocol6(AckedEchoProtocol):
    """TODO: like 2 but states *yield* out events and *return* next state."""


##


"""
TODO:
 - if receive 'prefix <s>' change echo prefix
 - if receive 'rev' reverse all output
 - if receive 'dup' output n lines
 - if receive 'seal' forbid further configuration (preferably in a new state)
"""


def _main() -> None:
    input_buf = b'hi0\nhi1\nhi\nthere\n'

    def handle_output(e: Event) -> None:
        if isinstance(e, SendLine):
            print(repr(e))
            return
        raise IllegalStateException

    for p in [
        AckedEchoProtocol0(),
        AckedEchoProtocol1(),
        AckedEchoProtocol2(),
        AckedEchoProtocol3(),
        AckedEchoProtocol4(),
        AckedEchoProtocol5(),
    ]:
        print(p)

        spl = random.randint(1, 1 + len(input_buf) - 2)
        ibs = [input_buf[:spl], input_buf[spl:]]
        print(ibs)

        lr = LineReader()
        for ib in ibs:
            for le in lr.accept(RecvdData(ib)):
                for oe in p.accept(le):
                    handle_output(oe)

        print()


if __name__ == '__main__':
    _main()
