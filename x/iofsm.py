"""
TODO:
 - ** i remember thinking about resource disposal at some point.. make sure everything 'closes'? **
 - LineReader + BufferedWriter
"""
import abc
import dataclasses as dc
import random
import typing as ta

from omlish import cached
from omlish import lang


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
    """
    TODO:
     - max length (ircproto is 510)
    """

    def __init__(self) -> None:
        super().__init__()
        self._buf = bytearray()

    def __call__(self, e: Event) -> ta.Iterable[Event]:
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

    @abc.abstractmethod
    def __call__(self, e: Event) -> ta.Iterable[Event]:
        raise NotImplementedError


#


class AckedEchoProtocol0(AckedEchoProtocol):
    def __init__(self) -> None:
        super().__init__()
        self._state = 0

    def __call__(self, e: Event) -> ta.Iterable[Event]:
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
        self._accept = self._accept_0

    def __call__(self, e: Event) -> ta.Iterable[Event]:
        return self._accept(e)

    def _accept_0(self, e: Event) -> ta.Iterable[Event]:
        if isinstance(e, RecvdLine):
            if e.line == self.ACK0:
                self._accept = self._accept_1
                return []
        raise IllegalStateException

    def _accept_1(self, e: Event) -> ta.Iterable[Event]:
        if isinstance(e, RecvdLine):
            if e.line == self.ACK1:
                self._accept = self._accept_2
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

    def __call__(self, e: Event) -> ta.Iterable[Event]:
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

    def __call__(self, e: Event) -> ta.Iterable[Event]:
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

    def __call__(self, e: Event) -> ta.Iterable[Event]:
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


EventGenerator: ta.TypeAlias = ta.Generator[ta.Iterable[Event] | None, Event, ta.Optional['EventGenerator']]


class AckedEchoProtocol5(AckedEchoProtocol):
    """like 4 but can switch acceptor gens."""

    def __init__(self) -> None:
        super().__init__()
        self._gen: EventGenerator | None = self._accept_0()
        if (n := next(self._gen)) is not None:  # noqa
            raise IllegalStateException

    def __call__(self, e: Event) -> ta.Iterable[Event]:
        if self._gen is None:
            raise IllegalStateException
        try:
            while (o := self._gen.send(e)) is not None:
                yield from o
        except StopIteration as s:
            if s.value is None:
                raise IllegalStateException
            self._gen = s.value
            if (n := next(self._gen)) is not None:  # noqa
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


##


I = ta.TypeVar('I')
O = ta.TypeVar('O')

# MachineGen: ta.TypeAlias = ta.Generator[ta.Iterable[O] | None, I, ta.Optional[MachineGen[I, O]]]
MachineGen = ta.Generator  # ta.TypeAlias


class Machine(ta.Generic[I, O]):
    def __init__(self, initial: MachineGen) -> None:
        super().__init__()
        self._advance(initial)

    _gen: MachineGen

    def _advance(self, gen: MachineGen) -> None:
        self._gen = gen
        if (n := next(self._gen)) is not None:  # noqa
            raise IllegalStateException

    def __call__(self, i: I) -> ta.Iterable[O]:
        if self._gen is None:
            raise IllegalStateException
        try:
            while (o := self._gen.send(i)) is not None:
                yield from o
        except StopIteration as s:
            if s.value is None:
                raise IllegalStateException
            self._advance(s.value)


#


class AckedEchoProtocol6(AckedEchoProtocol):
    def __init__(self) -> None:
        super().__init__()
        self._m = Machine[Event, Event](self._accept_0())

    def __call__(self, e: Event) -> ta.Iterable[Event]:
        return self._m(e)

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


##


@dc.dataclass(frozen=True)
class AckedEchoProtocol7(AckedEchoProtocol):
    """ok now injectable!"""

    prefix: str = 'echo'

    @cached.property
    def _m(self) -> Machine[Event, Event]:
        return Machine(self._accept_0())

    def __call__(self, e: Event) -> ta.Iterable[Event]:
        return self._m(e)

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
                yield [SendLine(f'{self.prefix} ' + e.line)]
            else:
                raise IllegalStateException


##


class AckedEchoProtocol8(AckedEchoProtocol):
    """
    TODO:
     - if receive 'prefix <n>' change echo prefix
     - if receive 'rev' reverse all output
     - if receive 'dup' output n lines
     - if receive 'seal' forbid further configuration (preferably in a new state)
    """

    def __init__(self) -> None:
        super().__init__()

        self._prefix = 'echo'
        self._rev = False
        self._dup = 1

        self._m = Machine[Event, Event](self._accept_ack())

    def __call__(self, e: Event) -> ta.Iterable[Event]:
        return self._m(e)

    def _accept_ack(self) -> EventGenerator:
        for ack in [self.ACK0, self.ACK1]:
            e = yield
            if not isinstance(e, RecvdLine) and e.line == ack:
                raise IllegalStateException
        return self._accept_echo_unsealed()

    def _process_control(self, l: str) -> bool:
        if l.startswith('prefix '):
            _, self._prefix = l.strip().split(' ')
            return True
        elif l.strip() == 'rev':
            self._rev = not self._rev
            return True
        elif l.startswith('dup '):
            _, d = l.strip().split(' ')
            self._dup = int(d)
            return True
        else:
            return False

    def _accept_echo_unsealed(self) -> EventGenerator:
        while True:
            e = yield
            if isinstance(e, RecvdLine):
                if self._process_control(e.line):
                    continue
                elif e.line.strip() == 'seal':
                    return self._accept_sealed()
                else:
                    l = e.line
                    if self._rev:
                        l = l.strip()[::-1] + '\n'
                    for _ in range(self._dup):
                        yield [SendLine(f'{self._prefix} {l}')]
            else:
                raise IllegalStateException

    def _accept_sealed(self) -> EventGenerator:
        while True:
            e = yield
            if isinstance(e, RecvdLine):
                l = e.line
                if self._rev:
                    l = l.strip()[::-1] + '\n'
                for _ in range(self._dup):
                    yield [SendLine(f'{self._prefix} {l}')]
            else:
                raise IllegalStateException


##


class AckedEchoProtocol9(AckedEchoProtocol):
    """
    TODO:
     - if receive 'prefix <n>' change echo prefix
     - if receive 'rev' reverse all output
     - if receive 'dup' output n lines
     - if receive 'seal' *actually* forbid further configuration (preferably in a new state)
    """

    def __init__(self) -> None:
        super().__init__()

        self._prefix = 'echo'
        self._rev = False
        self._dup = 1

        self._m = Machine[Event, Event](self._accept_ack())

    def __call__(self, e: Event) -> ta.Iterable[Event]:
        return self._m(e)

    def _accept_ack(self) -> EventGenerator:
        for ack in [self.ACK0, self.ACK1]:
            e = yield
            if not isinstance(e, RecvdLine) and e.line == ack:
                raise IllegalStateException
        return self._accept_echo_unsealed()

    class _Control(abc.ABC):  # noqa
        pass

    @dc.dataclass(frozen=True)
    class _PrefixControl(_Control):
        prefix: str

    @dc.dataclass(frozen=True)
    class _RevControl(_Control):
        pass

    @dc.dataclass(frozen=True)
    class _DupControl(_Control):
        dup: int

    def _parse_control(self, l: str) -> _Control | None:
        if l.startswith('prefix '):
            _, p = l.strip().split(' ')
            return self._PrefixControl(p)
        elif l.strip() == 'rev':
            return self._RevControl()
        elif l.startswith('dup '):
            _, d = l.strip().split(' ')
            return self._DupControl(int(d))
        else:
            return None

    def _apply_control(self, c: _Control) -> None:
        if isinstance(c, self._PrefixControl):
            self._prefix = c.prefix
        elif isinstance(c, self._RevControl):
            self._rev = not self._rev
        elif isinstance(c, self._DupControl):
            self._dup = c.dup
        else:
            raise TypeError(c)

    def _yield_echo(self, l: str) -> ta.Iterator[Event]:
        if self._rev:
            l = l.strip()[::-1] + '\n'
        for _ in range(self._dup):
            yield [SendLine(f'{self._prefix} {l}')]

    def _accept_echo_unsealed(self) -> EventGenerator:
        while True:
            e = yield
            if isinstance(e, RecvdLine):
                if (c := self._parse_control(e.line)) is not None:
                    self._apply_control(c)
                    continue
                elif e.line.strip() == 'seal':
                    return self._accept_sealed()
                else:
                    yield from self._yield_echo(e.line)
            else:
                raise IllegalStateException

    def _accept_sealed(self) -> EventGenerator:
        while True:
            e = yield
            if isinstance(e, RecvdLine):
                if (c := self._parse_control(e.line)) is not None:  # noqa
                    raise IllegalStateException
                yield from self._yield_echo(e.line)
            else:
                raise IllegalStateException


##


def _main() -> None:
    def handle_output(e: Event) -> None:
        if isinstance(e, SendLine):
            print(repr(e))
            return
        raise IllegalStateException

    ##

    input_buf = b'\n'.join([
        b'hi0',
        b'hi1',

        b'hi',
        b'there',

        b'rev',
        b'hi',
        b'there',

        b'dup 2',
        b'hi',
        b'there',

        b'prefix foo',
        b'hi',
        b'there',

        b'seal',
        b'hi',
        b'there',

        b'dup 3',
        b'',
    ])

    for p in [
        # AckedEchoProtocol0(),
        # AckedEchoProtocol1(),
        # AckedEchoProtocol2(),
        # AckedEchoProtocol3(),
        # AckedEchoProtocol4(),
        # AckedEchoProtocol5(),
        # AckedEchoProtocol6(),
        # AckedEchoProtocol7(),
        # AckedEchoProtocol8(),
        AckedEchoProtocol9(),
    ]:
        print(p)

        spl = random.randint(1, 1 + len(input_buf) - 2)
        ibs = list(map(RecvdData, [input_buf[:spl], input_buf[spl:]]))  # noqa
        print(ibs)

        lr = LineReader()

        # for ib in ibs:
        #     for le in lr(ib):
        #         for oe in p(le):
        #             handle_output(oe)

        # g = (
        #     oe
        #     for ib in ibs
        #     for le in lr(ib)
        #     for oe in p(le)
        # )

        les = lang.flatmap(lr, ibs)
        oes = lang.flatmap(p, les)

        for oe in oes:
            handle_output(oe)

        print()


if __name__ == '__main__':
    _main()
