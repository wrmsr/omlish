# ruff: noqa: UP007
# @omlish-lite
# Based on bluelet ( https://github.com/sampsyo/bluelet ) by Adrian Sampson, original license:
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import abc
import dataclasses as dc
import typing as ta


R = ta.TypeVar('R')

BlueletEventT = ta.TypeVar('BlueletEventT', bound='BlueletEvent')  # ta.TypeAlias

BlueletWaitable = ta.Union[int, 'BlueletHasFileno']  # ta.TypeAlias


##


class BlueletEvent(abc.ABC):  # noqa
    """
    Just a base class identifying Bluelet events. An event is an object yielded from a Bluelet coro coroutine to
    suspend operation and communicate with the scheduler.
    """

    def __await__(self):
        return BlueletFuture(self).__await__()


##


class BlueletHasFileno(ta.Protocol):
    def fileno(self) -> int: ...


@dc.dataclass(frozen=True)
class BlueletWaitables:
    r: ta.Sequence[BlueletWaitable] = ()
    w: ta.Sequence[BlueletWaitable] = ()
    x: ta.Sequence[BlueletWaitable] = ()


class WaitableBlueletEvent(BlueletEvent, abc.ABC):  # noqa
    """
    A waitable event is one encapsulating an action that can be waited for using a select() call. That is, it's an event
    with an associated file descriptor.
    """

    def waitables(self) -> BlueletWaitables:
        """
        Return "waitable" objects to pass to select(). Should return three iterables for input readiness, output
        readiness, and exceptional conditions (i.e., the three lists passed to select()).
        """
        return BlueletWaitables()

    def fire(self) -> ta.Any:
        """Called when an associated file descriptor becomes ready (i.e., is returned from a select() call)."""


##


@dc.dataclass(eq=False)
class BlueletFuture(ta.Generic[BlueletEventT, R]):
    event: BlueletEventT
    done: bool = False
    result: ta.Optional[R] = None

    def __await__(self):
        if not self.done:
            yield self
        if not self.done:
            raise RuntimeError("await wasn't used with event future")
        return self.result
