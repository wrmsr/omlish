# Based on bluelet ( https://github.com/sampsyo/bluelet ) by Adrian Sampson, original license:
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ruff: noqa: UP007
import abc
import dataclasses as dc
import typing as ta

from .core import DelegationBlueletEvent
from .core import ReturnBlueletEvent
from .events import BlueletEvent
from .events import BlueletWaitables
from .events import WaitableBlueletEvent


##


class FileBlueletEvent(BlueletEvent, abc.ABC):
    pass


##


@dc.dataclass(frozen=True, eq=False)
class ReadBlueletEvent(WaitableBlueletEvent, FileBlueletEvent):
    """Reads from a file-like object."""

    fd: ta.IO
    bufsize: int

    def waitables(self) -> BlueletWaitables:
        return BlueletWaitables(r=[self.fd])

    def fire(self) -> bytes:
        return self.fd.read(self.bufsize)


def bluelet_read(fd: ta.IO, bufsize: ta.Optional[int] = None) -> BlueletEvent:
    """Event: read from a file descriptor asynchronously."""

    if bufsize is None:
        # Read all.
        def reader():
            buf = []
            while True:
                data = yield bluelet_read(fd, 1024)
                if not data:
                    break
                buf.append(data)
            yield ReturnBlueletEvent(''.join(buf))

        return DelegationBlueletEvent(reader())

    else:
        return ReadBlueletEvent(fd, bufsize)


##


@dc.dataclass(frozen=True, eq=False)
class WriteBlueletEvent(WaitableBlueletEvent, FileBlueletEvent):
    """Writes to a file-like object."""

    fd: ta.IO
    data: bytes

    def waitables(self) -> BlueletWaitables:
        return BlueletWaitables(w=[self.fd])

    def fire(self) -> None:
        self.fd.write(self.data)


def bluelet_write(fd: ta.IO, data: bytes) -> BlueletEvent:
    """Event: write to a file descriptor asynchronously."""

    return WriteBlueletEvent(fd, data)
