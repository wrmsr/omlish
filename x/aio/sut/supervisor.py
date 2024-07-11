import dataclasses as dc
import enum
import itertools
import random
import time
import typing as ta

from omlish import lang
import anyio.abc

from .events import Event
from .events import EventHook
from .types import CancelFunc
from .types import Context
from .types import Duration
from .types import Service
from .types import ServiceId
from .types import ServiceToken
from .types import Supervisor
from .types import SupervisorId
from .types import Time
from .types import UnstoppedServiceReport


##


type Jitter = ta.Callable[[Duration], Duration]


def no_jitter(d: Duration) -> Duration:
    return d


def default_jitter(d: Duration) -> Duration:
    # uniformly distribute it into the range [FailureBackoff, 1.5 * FailureBackoff).
    jitter = random.random() / 2.
    return d + (d * jitter)


##


def print_event(e: Event) -> None:
    print(e)


@dc.dataclass(frozen=True)
class Spec(lang.Final):
    event_hook: EventHook | None = print_event
    failure_decay: float = 30.
    failure_threshold: float = 5.
    failure_backoff: Duration = 15.
    backoff_jitter: Jitter = default_jitter
    timeout: Duration = 10.
    pass_through_panics: bool = False
    dont_propagate_termination: bool = False


##


_SUPERVISOR_ID_SEQ = itertools.count()


def _next_supervisor_id() -> SupervisorId:
    return SupervisorId(next(_SUPERVISOR_ID_SEQ))


class SupervisorState(enum.Enum):
    NOT_RUNNING = enum.auto()
    NORMAL = enum.auto()
    PAUSED = enum.auto()
    TERMINATED = enum.auto()


@dc.dataclass(frozen=True)
class ServiceWithName(lang.Final):
    service: Service
    name: str


class SupervisorImpl(Supervisor):
    def __init__(self, name: str, spec: Spec) -> None:
        super().__init__()
        
        self._name = name
        self._spec = spec

        self._services: dict[ServiceId, ServiceWithName] = {}
        self._cancellations: dict[ServiceId, CancelFunc] = {}
        self._services_shutting_down: dict[ServiceId, ServiceWithName] = {}
        
        self._last_fail: Time = 0.

        self._failures = 0.
        
        # restartQueue         []serviceId = make([]serviceId, 0, 1),
        
        self._service_counter: ServiceId = ServiceId(0)
        
        # control              chan supervisorMessage = make(chan supervisorMessage),
        
        # notifyServiceDone    chan serviceId = make(chan serviceId),
        
        # resumeTimer          <-chan time.Time = make(chan time.Time),
        
        # liveness             chan struct{} = make(chan struct{}),

        # despite the recommendation in the context package to avoid holding this in a struct, I think due to the
        # function of suture and the way it works, I think it's OK in this case. This is the exceptional case,
        # basically.
        self._ctx_mutex = anyio.Lock()
        # ctx      context.Context = nil,

        # This function cancels this supervisor specifically.
        self._ctx_cancel: CancelFunc | None = None

        self._get_now: ta.Callable[[], Time] = time.time
        
        # getAfterChan func(Duration) <-chan time.Time = time.After

        self._m = anyio.Lock()

        # The unstopped service report is generated when we finish stopping.
        self._unstopped_service_report: UnstoppedServiceReport = []

        self._id = _next_supervisor_id()

        self._state: SupervisorState = SupervisorState.NOT_RUNNING

    async def add(self, service: Service) -> ServiceToken:
        pass

    async def serve_background(self, ctx: Context) -> anyio.abc.ObjectReceiveStream[Exception]:
        pass

    async def serve(self, ctx: Context) -> Exception:
        pass

    async def unstopped_service_report(self) -> tuple[UnstoppedServiceReport, Exception]:
        pass

    async def remove(self, id: ServiceToken) -> Exception:
        pass

    async def remove_and_wait(self, id: ServiceToken, timeout: Duration) -> Exception:
        pass

    async def services(self) -> list[Service]:
        pass
