"""
TODO:
 - amalgify? prefix everything w/ Blue? prob want some helper Namespace or smth
"""
# @omlish-lite
# Based on bluelet by Adrian Sampson, original license:
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# https://github.com/sampsyo/bluelet

from .core import (  # noqa
    CoreEvent,
    Coro,
    DelegationEvent,
    ExcInfo,
    ExceptionEvent,
    JoinEvent,
    KillEvent,
    ReturnEvent,
    SleepEvent,
    SpawnEvent,
    ValueEvent,
    call,
    end,
    join,
    kill,
    null,
    sleep,
    spawn,
)

from .events import (  # noqa
    Event,
    HasFileno,
    Waitable,
    WaitableEvent,
    Waitables,
)

from .files import (  # noqa
    FileEvent,
    ReadEvent,
    WriteEvent,
    read,
    write,
)

from .run_ import (  # noqa
    run,
    ThreadException,
)

from .sockets import (   # noqa
    AcceptEvent,
    Connection,
    Listener,
    ReceiveEvent,
    SendEvent,
    SocketClosedError,
    SocketEvent,
    connect,
    server,
)
