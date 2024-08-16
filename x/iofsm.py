import abc
import dataclasses as dc


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
class SendLine(InputEvent):
    line: str


##


class AckedEchoProtocol:
    pass


##


def _main():
    pass


if __name__ == '__main__':
    _main()
