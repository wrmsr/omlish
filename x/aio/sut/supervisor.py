import dataclasses as dc
import enum
import itertools
import random
import time
import typing as ta

from omlish import lang
from omlish.asyncs import anyio as aiu
import anyio.abc

from .events import Event
from .events import EventHook
from .messages import SupervisorMessage
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
        
        self._restart_queue: list[ServiceId] = []
        
        self._service_counter: ServiceId = ServiceId(0)

        self._control = aiu.staple_memory_object_stream(*anyio.create_memory_object_stream[SupervisorMessage]())
        self._notify_service_done = aiu.staple_memory_object_stream(*anyio.create_memory_object_stream[ServiceId]())
        self._resume_timer = aiu.staple_memory_object_stream(*anyio.create_memory_object_stream[Time]())
        self._liveness = anyio.Event()

        # despite the recommendation in the context package to avoid holding this in a struct, I think due to the
        # function of suture and the way it works, I think it's OK in this case. This is the exceptional case,
        # basically.
        self._ctx_mutex = anyio.Lock()
        self._ctx: Context | None = None

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
        """
        if s == nil {
            panic("can't add service to nil *suture.Supervisor")
        }

        if hasSupervisor, isHaveSupervisor := service.(HasSupervisor); isHaveSupervisor {
            supervisor := hasSupervisor.GetSupervisor()
            if supervisor != nil {
                supervisor.spec.EventHook = s.spec.EventHook
            }
        }

        s.m.Lock()
        if s.state == notRunning {
            id := s.serviceCounter
            s.serviceCounter++

            s.services[id] = serviceWithName{service, serviceName(service)}
            s.restartQueue = append(s.restartQueue, id)

            s.m.Unlock()
            return ServiceToken{supervisor: s.id, service: id}
        }
        s.m.Unlock()

        response := make(chan serviceID)
        if s.sendControl(addService{service, serviceName(service), response}) != nil {
            return ServiceToken{}
        }
        return ServiceToken{supervisor: s.id, service: <-response}
        """

    async def serve_background(self, ctx: Context) -> anyio.abc.ObjectReceiveStream[Exception]:
        """
        errChan := make(chan error, 1)
        go func() {
            errChan <- s.Serve(ctx)
        }()
        s.sync()
        return errChan
        """

    async def serve(self, ctx: Context) -> Exception | None:
        """
        // context documentation suggests that it is legal for functions to
        // take nil contexts, it's user's responsibility to never pass them in.
        if ctx == nil {
            ctx = context.Background()
        }

        if s == nil {
            panic("Can't serve with a nil *suture.Supervisor")
        }
        // Take a separate cancellation function so this tree can be
        // indepedently cancelled.
        ctx, myCancel := context.WithCancel(ctx)
        s.ctxMutex.Lock()
        s.ctx = ctx
        s.ctxMutex.Unlock()
        s.ctxCancel = myCancel

        if s.id == 0 {
            panic("Can't call Serve on an incorrectly-constructed *suture.Supervisor")
        }

        s.m.Lock()
        if s.state == normal || s.state == paused {
            s.m.Unlock()
            panic("Called .Serve() on a supervisor that is already Serve()ing")
        }

        s.state = normal
        s.m.Unlock()

        defer func() {
            s.m.Lock()
            s.state = terminated
            s.m.Unlock()
        }()

        // for all the services I currently know about, start them
        for _, id := range s.restartQueue {
            namedService, present := s.services[id]
            if present {
                s.runService(ctx, namedService.Service, id)
            }
        }
        s.restartQueue = make([]serviceID, 0, 1)

        for {
            select {
            case <-ctx.Done():
                s.stopSupervisor()
                return ctx.Err()
            case m := <-s.control:
                switch msg := m.(type) {
                case serviceFailed:
                    s.handleFailedService(ctx, msg.id, msg.panicVal, msg.stacktrace, true)
                case serviceEnded:
                    _, monitored := s.services[msg.id]
                    if monitored {
                        cancel := s.cancellations[msg.id]
                        if isErr(msg.err, ErrDoNotRestart) || isErr(msg.err, context.Canceled) || isErr(msg.err, context.DeadlineExceeded) {
                            delete(s.services, msg.id)
                            delete(s.cancellations, msg.id)
                            go cancel()
                        } else if isErr(msg.err, ErrTerminateSupervisorTree) {
                            s.stopSupervisor()
                            if s.spec.DontPropagateTermination {
                                return ErrDoNotRestart
                            } else {
                                return msg.err
                            }
                        } else {
                            s.handleFailedService(ctx, msg.id, msg.err, nil, false)
                        }
                    }
                case addService:
                    id := s.serviceCounter
                    s.serviceCounter++

                    s.services[id] = serviceWithName{msg.service, msg.name}
                    s.runService(ctx, msg.service, id)

                    msg.response <- id
                case removeService:
                    s.removeService(msg.id, msg.notification)
                case stopSupervisor:
                    msg.done <- s.stopSupervisor()
                    return nil
                case listServices:
                    services := []Service{}
                    for _, service := range s.services {
                        services = append(services, service.Service)
                    }
                    msg.c <- services
                case syncSupervisor:
                    // this does nothing on purpose; its sole purpose is to
                    // introduce a sync point via the channel receive
                case panicSupervisor:
                    // used only by tests
                    panic("Panicking as requested!")
                }
            case serviceEnded := <-s.notifyServiceDone:
                delete(s.servicesShuttingDown, serviceEnded)
            case <-s.resumeTimer:
                // We're resuming normal operation after a pause due to
                // excessive thrashing
                // FIXME: Ought to permit some spacing of these functions, rather
                // than simply hammering through them
                s.m.Lock()
                s.state = normal
                s.m.Unlock()
                s.failures = 0
                s.spec.EventHook(EventResume{s, s.Name})
                for _, id := range s.restartQueue {
                    namedService, present := s.services[id]
                    if present {
                        s.runService(ctx, namedService.Service, id)
                    }
                }
                s.restartQueue = make([]serviceID, 0, 1)
            }
        }
        """

    async def unstopped_service_report(self) -> tuple[UnstoppedServiceReport, Exception | None]:
        await self._liveness.wait()

        # FIXME: Recurse on the supervisors
        return self._unstopped_service_report, None

    async def remove(self, id: ServiceToken) -> Exception | None:
        raise NotImplementedError

    async def remove_and_wait(self, id: ServiceToken, timeout: Duration) -> Exception | None:
        raise NotImplementedError

    async def services(self) -> list[Service]:
        raise NotImplementedError

"""
func (s *Supervisor) handleFailedService(ctx context.Context, id serviceID, err interface{}, stacktrace []byte, panic bool) {
    now := s.getNow()

    if s.lastFail.IsZero() {
        s.lastFail = now
        s.failures = 1.0
    } else {
        sinceLastFail := now.Sub(s.lastFail).Seconds()
        intervals := sinceLastFail / s.spec.FailureDecay
        s.failures = s.failures*math.Pow(.5, intervals) + 1
    }

    if s.failures > s.spec.FailureThreshold {
        s.m.Lock()
        s.state = paused
        s.m.Unlock()
        s.spec.EventHook(EventBackoff{s, s.Name})
        s.resumeTimer = s.getAfterChan(
            s.spec.BackoffJitter.Jitter(s.spec.FailureBackoff))
    }

    s.lastFail = now

    failedService, monitored := s.services[id]

    // It is possible for a service to be no longer monitored
    // by the time we get here. In that case, just ignore it.
    if monitored {
        s.m.Lock()
        curState := s.state
        s.m.Unlock()
        if curState == normal {
            s.runService(ctx, failedService.Service, id)
        } else {
            s.restartQueue = append(s.restartQueue, id)
        }
        if panic {
            s.spec.EventHook(EventServicePanic{
                Supervisor:       s,
                SupervisorName:   s.Name,
                Service:          failedService.Service,
                ServiceName:      failedService.name,
                CurrentFailures:  s.failures,
                FailureThreshold: s.spec.FailureThreshold,
                Restarting:       curState == normal,
                PanicMsg:         s.spec.Sprint(err),
                Stacktrace:       string(stacktrace),
            })
        } else {
            e := EventServiceTerminate{
                Supervisor:       s,
                SupervisorName:   s.Name,
                Service:          failedService.Service,
                ServiceName:      failedService.name,
                CurrentFailures:  s.failures,
                FailureThreshold: s.spec.FailureThreshold,
                Restarting:       curState == normal,
            }
            if err != nil {
                e.Err = err
            }
            s.spec.EventHook(e)
        }
    }
}

func (s *Supervisor) runService(ctx context.Context, service Service, id serviceID) {
    childCtx, cancel := context.WithCancel(ctx)
    done := make(chan struct{})
    blockingCancellation := func() {
        cancel()
        <-done
    }
    s.cancellations[id] = blockingCancellation
    go func() {
        if !s.spec.PassThroughPanics {
            defer func() {
                if r := recover(); r != nil {
                    buf := make([]byte, 65535)
                    written := runtime.Stack(buf, false)
                    buf = buf[:written]
                    s.fail(id, r, buf)
                }
            }()
        }

        var err error

        defer func() {
            cancel()
            close(done)

            r := recover()
            if r == nil {
                s.serviceEnded(id, err)
            } else {
                panic(r)
            }
        }()

        err = service.Serve(childCtx)
    }()
}

func (s *Supervisor) removeService(id serviceID, notificationChan chan struct{}) {
    namedService, present := s.services[id]
    if present {
        cancel := s.cancellations[id]
        delete(s.services, id)
        delete(s.cancellations, id)

        s.servicesShuttingDown[id] = namedService
        go func() {
            successChan := make(chan struct{})
            go func() {
                cancel()
                close(successChan)
                if notificationChan != nil {
                    notificationChan <- struct{}{}
                }
            }()

            select {
            case <-successChan:
                // Life is good!
            case <-s.getAfterChan(s.spec.Timeout):
                s.spec.EventHook(EventStopTimeout{
                    s, s.Name,
                    namedService.Service, namedService.name})
            }
            s.notifyServiceDone <- id
        }()
    } else {
        if notificationChan != nil {
            notificationChan <- struct{}{}
        }
    }
}

func (s *Supervisor) stopSupervisor() UnstoppedServiceReport {
    notifyDone := make(chan serviceID, len(s.services))

    for id, namedService := range s.services {
        cancel := s.cancellations[id]
        delete(s.services, id)
        delete(s.cancellations, id)
        s.servicesShuttingDown[id] = namedService
        go func(sID serviceID) {
            cancel()
            notifyDone <- sID
        }(id)
    }

    timeout := s.getAfterChan(s.spec.Timeout)

SHUTTING_DOWN_SERVICES:
    for len(s.servicesShuttingDown) > 0 {
        select {
        case id := <-notifyDone:
            delete(s.servicesShuttingDown, id)
        case serviceID := <-s.notifyServiceDone:
            delete(s.servicesShuttingDown, serviceID)
        case <-timeout:
            for _, namedService := range s.servicesShuttingDown {
                s.spec.EventHook(EventStopTimeout{
                    s, s.Name,
                    namedService.Service, namedService.name,
                })
            }

            // failed remove statements will log the errors.
            break SHUTTING_DOWN_SERVICES
        }
    }

    // If nothing else has cancelled our context, we should now.
    s.ctxCancel()

    // Indicate that we're done shutting down
    defer close(s.liveness)

    if len(s.servicesShuttingDown) == 0 {
        return nil
    } else {
        report := UnstoppedServiceReport{}
        for serviceID, serviceWithName := range s.servicesShuttingDown {
            report = append(report, UnstoppedService{
                SupervisorPath: []*Supervisor{s},
                Service:        serviceWithName.Service,
                Name:           serviceWithName.name,
                ServiceToken:   ServiceToken{supervisor: s.id, service: serviceID},
            })
        }
        s.m.Lock()
        s.unstoppedServiceReport = report
        s.m.Unlock()
        return report
    }
}
"""