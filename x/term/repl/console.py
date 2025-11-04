#   Copyright 2000-2004 Michael Hudson-Doyle <micahel@gmail.com>
#
#                    All Rights Reserved
#
#
# Permission to use, copy, modify, and distribute this software and its documentation for any purpose is hereby granted
# without fee, provided that the above copyright notice appear in all copies and that both that copyright notice and
# this permission notice appear in supporting documentation.
#
# THE AUTHOR MICHAEL HUDSON DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES
# OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
import abc
import dataclasses as dc
import errno
import sys
import termios
import typing as ta

from omlish import lang


##


class InvalidTerminal(RuntimeError):  # noqa
    def __init__(self, message: str) -> None:
        super().__init__(errno.EIO, message)


CONSOLE_ERROR_TYPES = (
    termios.error,
    InvalidTerminal,
)


##


@dc.dataclass()
class ConsoleEvent(lang.Final):
    evt: str
    data: str | None
    raw: bytes = b''


class Console(lang.Abstract):
    def __init__(
            self,
            f_in: ta.IO[bytes] | int = 0,
            f_out: ta.IO[bytes] | int = 1,
            term: str = '',
            encoding: str = '',
    ) -> None:
        super().__init__()

        self._encoding = encoding or sys.getdefaultencoding()

        if isinstance(f_in, int):
            self._input_fd = f_in
        else:
            self._input_fd = f_in.fileno()

        if isinstance(f_out, int):
            self._output_fd = f_out
        else:
            self._output_fd = f_out.fileno()

        self._height: int = 25
        self._width: int = 80

        self._posxy: tuple[int, int] = (0, 0)

        self._screen: list[str] = []

    @property
    def encoding(self) -> str:
        return self._encoding

    @property
    def input_fd(self) -> int:
        return self._input_fd

    @property
    def output_fd(self) -> int:
        return self._output_fd

    @property
    def height(self) -> int:
        return self._height

    @property
    def width(self) -> int:
        return self._width

    @property
    def posxy(self) -> tuple[int, int]:
        return self._posxy

    def set_posxy(self, x: int, y: int) -> None:
        self._posxy = (x, y)

    @property
    def screen(self) -> list[str]:
        return self._screen

    def set_screen(self, screen: list[str]) -> None:
        self._screen = screen

    #

    @abc.abstractmethod
    def refresh(self, screen: list[str], xy: tuple[int, int]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def prepare(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def restore(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def move_cursor(self, x: int, y: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def set_cursor_vis(self, visible: bool) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def getheightwidth(self) -> tuple[int, int]:
        """
        Return (height, width) where height and width are the height and width of the terminal window in characters.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def get_event(self, block: bool = True) -> ConsoleEvent | None:
        """
        Return an Event instance. Returns None if |block| is false and there is no event pending, otherwise waits for
        the completion of an event.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def push_char(self, char: int | bytes) -> None:
        """Push a character to the console event queue."""

        raise NotImplementedError

    @abc.abstractmethod
    def beep(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def clear(self) -> None:
        """Wipe the screen"""

        raise NotImplementedError

    @abc.abstractmethod
    def finish(self) -> None:
        """
        Move the cursor to the end of the display and otherwise get ready for end.

        XXX could be merged with restore?  Hmm.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def flushoutput(self) -> None:
        """Flush all output to the screen (assuming there's some buffering going on somewhere)."""

        raise NotImplementedError

    @abc.abstractmethod
    def forgetinput(self) -> None:
        """Forget all pending, but not yet processed input."""

        raise NotImplementedError

    @abc.abstractmethod
    def getpending(self) -> ConsoleEvent:
        """Return the characters that have been typed but not yet processed."""

        raise NotImplementedError

    @abc.abstractmethod
    def wait(self, timeout: float | None) -> bool:
        """
        Wait for an event. The return value is True if an event is available, False if the timeout has been reached. If
        timeout is None, wait forever. The timeout is in milliseconds.
        """

        raise NotImplementedError

    @property
    @abc.abstractmethod
    def input_hook(self) -> ta.Callable[[], int] | None:
        """Returns the current input hook."""

        raise NotImplementedError

    @abc.abstractmethod
    def repaint(self) -> None:
        raise NotImplementedError
