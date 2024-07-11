import abc
import dataclasses as dc
import enum
import enum
import random
import typing as ta

from omlish import lang

from .events import Event
from .events import EventHook
from .types import Duration
from .types import Service
from .types import Supervisor


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


"""
class SupervisorState(enum.Enum):
    NOT_RUNNING = enum.auto()
    NORMAL = enum.auto()
    PAUSED = enum.auto()
    TERMINATED = enum.auto()


class SupervisorImpl(Supervisor):
    def __init__(self, name: str, spec: Spec) -> None:
        super().__init__()
        
        self._name = name
        self._spec = spec

        services             map[serviceID]serviceWithName
        make(map[serviceID]serviceWithName),
        
        cancellations        map[serviceID]context.CancelFunc
        make(map[serviceID]context.CancelFunc),
        
        servicesShuttingDown map[serviceID]serviceWithName
        make(map[serviceID]serviceWithName),
        
        lastFail             time.Time
        time.Time{},

        failures             float64
        0
        
        restartQueue         []serviceID
        make([]serviceID, 0, 1),
        
        serviceCounter       serviceID
        0,
        
        control              chan supervisorMessage
        make(chan supervisorMessage),
        
        notifyServiceDone    chan serviceID
        make(chan serviceID),
        
        resumeTimer          <-chan time.Time
        make(chan time.Time),
        
        liveness             chan struct{}
        make(chan struct{}),

        // despite the recommendation in the context package to avoid
        // holding this in a struct, I think due to the function of suture
        // and the way it works, I think it's OK in this case. This is the
        // exceptional case, basically.
        ctxMutex sync.Mutex
        sync.Mutex{},

        ctx      context.Context
        nil,

        // This function cancels this supervisor specifically.
        ctxCancel func()
        nil

        getNow       func() time.Time
        time.Now
        
        getAfterChan func(Duration) <-chan time.Time
        time.After

        m sync.Mutex
        sync.Mutex{},

        // The unstopped service report is generated when we finish
        // stopping.
        unstoppedServiceReport UnstoppedServiceReport

        // malign leftovers
        id    supervisorID
        nextSupervisorID(),

        self._state: SupervisorState = SupervisorState.NOT_RUNNING
"""
