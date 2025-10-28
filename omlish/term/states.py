import dataclasses as dc
import termios


##


@dc.dataclass()
class TermState:
    iflag: int
    oflag: int
    cflag: int
    lflag: int
    ispeed: int
    ospeed: int
    cc: list[bytes]

    #

    def copy(self) -> 'TermState':
        return TermState(*self.as_list())  # type: ignore[arg-type]

    def as_list(self) -> list[int | list[bytes]]:
        return [
            self.iflag,
            self.oflag,
            self.cflag,
            self.lflag,
            self.ispeed,
            self.ospeed,
            self.cc[:],
        ]


def get_term_state(fd: int) -> TermState:
    return TermState(*termios.tcgetattr(fd))


def set_term_state(fd: int, attrs: TermState, when: int = termios.TCSANOW) -> None:
    termios.tcsetattr(fd, when, attrs.as_list())


##


class TermStateStack:
    def __init__(self, fd: int = 0) -> None:  # noqa
        super().__init__()

        self._fd = fd
        self._stack: list[TermState] = []

    #

    def get(self) -> TermState:
        return get_term_state(self._fd)

    def set(self, attrs: TermState, when: int = termios.TCSANOW) -> None:
        set_term_state(self._fd, attrs, when)

    #

    def save(self) -> None:
        self._stack.append(self.get())

    def restore(self) -> None:
        self.set(self._stack.pop())
