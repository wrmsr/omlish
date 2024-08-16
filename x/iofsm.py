import abc
import dataclasses as dc
import typing as ta


##


class InputEvent(abc.ABC):
    pass


@dc.dataclass(frozen=True)
class RecvdLine(InputEvent):
    line: str


##


class OutputEvent(abc.ABC):
    pass


@dc.dataclass(frozen=True)
class SendLine(OutputEvent):
    line: str


##


class IllegalStateException(Exception):
    pass


class AckedEchoProtocol0:
    ACK0 = 'hi0'
    ACK1 = 'hi1'

    def __init__(self) -> None:
        super().__init__()
        self._state = 0

    def accept(self, ie: InputEvent) -> ta.Iterable[OutputEvent]:
        if self._state == 0:
            if isinstance(ie, RecvdLine):
                if ie.line == self.ACK0:
                    self._state = 1
                    return []
        if self._state == 1:
            if isinstance(ie, RecvdLine):
                if ie.line == self.ACK1:
                    self._state = 2
                    return []
        if self._state == 2:
            if isinstance(ie, RecvdLine):
                return [SendLine(ie.line)]
        raise IllegalStateException


##


def _main() -> None:
    def handle_output(oe: OutputEvent) -> None:
        if isinstance(oe, SendLine):
            print(oe.line)
            return
        raise IllegalStateException

    p = AckedEchoProtocol0()

    for ie in [
        RecvdLine('hi0'),
        RecvdLine('hi1'),
        RecvdLine('foo'),
        RecvdLine('bar'),
    ]:
        for oe in p.accept(ie):
            handle_output(oe)


if __name__ == '__main__':
    _main()
