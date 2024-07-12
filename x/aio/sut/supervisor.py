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
from .messages import AddService
from .messages import SupervisorMessage
from .types import CancelFunc
from .types import Context
from .types import Duration
from .types import HasSupervisor
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


@dc.dataclass()
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


class WrongSupervisor(Exception):
    """Returned by the Remove method if you pass a ServiceToken from the wrong Supervisor."""
    def __init__(self) -> None:
        super().__init__("wrong supervisor for this service token, no service removed")


class Timeout(Exception):
    """Returned when an attempt to RemoveAndWait for a service to stop has timed out."""
    def __init__(self) -> None:
        super().__init__("waiting for service to stop has timed out")


class SupervisorNotTerminated(Exception):
    """Returned when asking for a stopped service report before the supervisor has been terminated."""
    def __init__(self) -> None:
        super().__init__("supervisor not terminated")


class SupervisorNotStarted(Exception):
    """
    Returned if you try to send control messages to a supervisor that has not started yet. See note on Supervisor struct
    about the legal ways to start a supervisor.
    """
    def __init__(self) -> None:
        super().__init__("supervisor not started yet")


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


def _build_service_name(svc: Service) -> str:
    return f'{svc.__class__.__name__}@{hex(id(svc))[2:]}'


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

    def supervisor(self) -> Supervisor | None:
        return self

    async def _send_control(self, sm: SupervisorMessage) -> Exception | None:
        """
        # sendControl abstracts checking for the supervisor to still be running when we send a message. This prevents
        # blocking when sending to a cancelled supervisor.
        done_chan = aiu.staple_memory_object_stream(*anyio.create_memory_object_stream[ta.Any]())
        with self._ctx_mutex:
            if s.ctx == nil {
                return ErrSupervisorNotStarted
            }
            doneChan = s.ctx.Done()

        select {
        case s.control <- sm:
            return nil
        case <-doneChan:
            return ErrSupervisorNotRunning
        }
        """

    async def add(self, service: Service) -> ServiceToken:
        if isinstance(service, HasSupervisor):
            supervisor = service.supervisor()
            if supervisor is not None:
                supervisor._spec.event_hook = self._spec.event_hook  # noqa

        with self._m:
            if self._state == SupervisorState.NOT_RUNNING:
                sid = self._service_counter
                self._service_counter += 1

                self._services[sid] = ServiceWithName(service, _build_service_name(service))
                self._restart_queue.append(sid)

                return ServiceToken(self._id, sid)

        response = aiu.staple_memory_object_stream(*anyio.create_memory_object_stream[ServiceId]())
        if await self._send_control(AddService(service, _build_service_name(service), response)) is not None:
            return ServiceToken.ZERO

        return ServiceToken(self._id, await response.receive())

    async def serve_background(self, ctx: Context) -> anyio.abc.ObjectReceiveStream[Exception]:
        """
        errChan := make(chan error, 1)
        go func() {
            errChan <- self._Serve(ctx)
        }()
        self._sync()
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
        // independently cancelled.
        ctx, myCancel := context.WithCancel(ctx)
        self._ctxMutex.Lock()
        self._ctx = ctx
        self._ctxMutex.Unlock()
        self._ctxCancel = myCancel

        if self._id == 0 {
            panic("Can't call Serve on an incorrectly-constructed *suture.Supervisor")
        }

        self._m.Lock()
        if self._state == normal || self._state == paused {
            self._m.Unlock()
            panic("Called .Serve() on a supervisor that is already Serve()ing")
        }

        self._state = normal
        self._m.Unlock()

        defer func() {
            self._m.Lock()
            self._state = terminated
            self._m.Unlock()
        }()

        // for all the services I currently know about, start them
        for _, sid := range self._restartQueue {
            namedService, present := self._services[sid]
            if present {
                self._runService(ctx, namedService.Service, sid)
            }
        }
        self._restartQueue = make([]serviceID, 0, 1)

        for {
            select {
            case <-ctx.Done():
                self._stopSupervisor()
                return ctx.Err()
            case m := <-self._control:
                switch msg := m.(type) {
                case serviceFailed:
                    self._handleFailedService(ctx, msg.sid, msg.panicVal, msg.stacktrace, true)
                case serviceEnded:
                    _, monitored := self._services[msg.sid]
                    if monitored {
                        cancel := self._cancellations[msg.sid]
                        if isErr(msg.err, ErrDoNotRestart) || isErr(msg.err, context.Canceled) || isErr(msg.err, context.DeadlineExceeded) {
                            delete(self._services, msg.sid)
                            delete(self._cancellations, msg.sid)
                            go cancel()
                        } else if isErr(msg.err, ErrTerminateSupervisorTree) {
                            self._stopSupervisor()
                            if self._spec.DontPropagateTermination {
                                return ErrDoNotRestart
                            } else {
                                return msg.err
                            }
                        } else {
                            self._handleFailedService(ctx, msg.sid, msg.err, nil, false)
                        }
                    }
                case addService:
                    sid := self._serviceCounter
                    self._serviceCounter++

                    self._services[sid] = serviceWithName{msg.service, msg.name}
                    self._runService(ctx, msg.service, sid)

                    msg.response <- sid
                case removeService:
                    self._removeService(msg.sid, msg.notification)
                case stopSupervisor:
                    msg.done <- self._stopSupervisor()
                    return nil
                case listServices:
                    services := []Service{}
                    for _, service := range self._services {
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
            case serviceEnded := <-self._notifyServiceDone:
                delete(self._servicesShuttingDown, serviceEnded)
            case <-self._resumeTimer:
                // We're resuming normal operation after a pause due to
                // excessive thrashing
                // FIXME: Ought to permit some spacing of these functions, rather
                // than simply hammering through them
                self._m.Lock()
                self._state = normal
                self._m.Unlock()
                self._failures = 0
                self._spec.EventHook(EventResume{s, self._Name})
                for _, sid := range self._restartQueue {
                    namedService, present := self._services[sid]
                    if present {
                        self._runService(ctx, namedService.Service, sid)
                    }
                }
                self._restartQueue = make([]serviceID, 0, 1)
            }
        }
        """

    async def unstopped_service_report(self) -> tuple[UnstoppedServiceReport, Exception | None]:
        await self._liveness.wait()

        # FIXME: Recurse on the supervisors
        return self._unstopped_service_report, None

    async def remove(self, sid: ServiceToken) -> Exception | None:
        raise NotImplementedError

    async def remove_and_wait(self, sid: ServiceToken, timeout: Duration) -> Exception | None:
        raise NotImplementedError

    async def services(self) -> list[Service]:
        raise NotImplementedError

"""
func (s *Supervisor) handleFailedService(ctx context.Context, sid serviceID, err interface{}, stacktrace []byte, panic bool) {
    now := self._getNow()

    if self._lastFail.IsZero() {
        self._lastFail = now
        self._failures = 1.0
    } else {
        sinceLastFail := now.Sub(self._lastFail).Seconds()
        intervals := sinceLastFail / self._spec.FailureDecay
        self._failures = self._failures*math.Pow(.5, intervals) + 1
    }

    if self._failures > self._spec.FailureThreshold {
        self._m.Lock()
        self._state = paused
        self._m.Unlock()
        self._spec.EventHook(EventBackoff{s, self._Name})
        self._resumeTimer = self._getAfterChan(
            self._spec.BackoffJitter.Jitter(self._spec.FailureBackoff))
    }

    self._lastFail = now

    failedService, monitored := self._services[sid]

    // It is possible for a service to be no longer monitored
    // by the time we get here. In that case, just ignore it.
    if monitored {
        self._m.Lock()
        curState := self._state
        self._m.Unlock()
        if curState == normal {
            self._runService(ctx, failedService.Service, sid)
        } else {
            self._restartQueue = append(self._restartQueue, sid)
        }
        if panic {
            self._spec.EventHook(EventServicePanic{
                Supervisor:       s,
                SupervisorName:   self._Name,
                Service:          failedService.Service,
                ServiceName:      failedService.name,
                CurrentFailures:  self._failures,
                FailureThreshold: self._spec.FailureThreshold,
                Restarting:       curState == normal,
                PanicMsg:         self._spec.Sprint(err),
                Stacktrace:       string(stacktrace),
            })
        } else {
            e := EventServiceTerminate{
                Supervisor:       s,
                SupervisorName:   self._Name,
                Service:          failedService.Service,
                ServiceName:      failedService.name,
                CurrentFailures:  self._failures,
                FailureThreshold: self._spec.FailureThreshold,
                Restarting:       curState == normal,
            }
            if err != nil {
                e.Err = err
            }
            self._spec.EventHook(e)
        }
    }
}

func (s *Supervisor) runService(ctx context.Context, service Service, sid serviceID) {
    childCtx, cancel := context.WithCancel(ctx)
    done := make(chan struct{})
    blockingCancellation := func() {
        cancel()
        <-done
    }
    self._cancellations[sid] = blockingCancellation
    go func() {
        if !self._spec.PassThroughPanics {
            defer func() {
                if r := recover(); r != nil {
                    buf := make([]byte, 65535)
                    written := runtime.Stack(buf, false)
                    buf = buf[:written]
                    self._fail(sid, r, buf)
                }
            }()
        }

        var err error

        defer func() {
            cancel()
            close(done)

            r := recover()
            if r == nil {
                self._serviceEnded(sid, err)
            } else {
                panic(r)
            }
        }()

        err = service.Serve(childCtx)
    }()
}

func (s *Supervisor) removeService(sid serviceID, notificationChan chan struct{}) {
    namedService, present := self._services[sid]
    if present {
        cancel := self._cancellations[sid]
        delete(self._services, sid)
        delete(self._cancellations, sid)

        self._servicesShuttingDown[sid] = namedService
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
            case <-self._getAfterChan(self._spec.Timeout):
                self._spec.EventHook(EventStopTimeout{
                    s, self._Name,
                    namedService.Service, namedService.name})
            }
            self._notifyServiceDone <- sid
        }()
    } else {
        if notificationChan != nil {
            notificationChan <- struct{}{}
        }
    }
}

func (s *Supervisor) stopSupervisor() UnstoppedServiceReport {
    notifyDone := make(chan serviceID, len(self._services))

    for sid, namedService := range self._services {
        cancel := self._cancellations[sid]
        delete(self._services, sid)
        delete(self._cancellations, sid)
        self._servicesShuttingDown[sid] = namedService
        go func(sID serviceID) {
            cancel()
            notifyDone <- sID
        }(sid)
    }

    timeout := self._getAfterChan(self._spec.Timeout)

SHUTTING_DOWN_SERVICES:
    for len(self._servicesShuttingDown) > 0 {
        select {
        case sid := <-notifyDone:
            delete(self._servicesShuttingDown, sid)
        case serviceID := <-self._notifyServiceDone:
            delete(self._servicesShuttingDown, serviceID)
        case <-timeout:
            for _, namedService := range self._servicesShuttingDown {
                self._spec.EventHook(EventStopTimeout{
                    s, self._Name,
                    namedService.Service, namedService.name,
                })
            }

            // failed remove statements will log the errors.
            break SHUTTING_DOWN_SERVICES
        }
    }

    // If nothing else has cancelled our context, we should now.
    self._ctxCancel()

    // Indicate that we're done shutting down
    defer close(self._liveness)

    if len(self._servicesShuttingDown) == 0 {
        return nil
    } else {
        report := UnstoppedServiceReport{}
        for serviceID, serviceWithName := range self._servicesShuttingDown {
            report = append(report, UnstoppedService{
                SupervisorPath: []*Supervisor{s},
                Service:        serviceWithName.Service,
                Name:           serviceWithName.name,
                ServiceToken:   ServiceToken{supervisor: self._id, service: serviceID},
            })
        }
        self._m.Lock()
        self._unstoppedServiceReport = report
        self._m.Unlock()
        return report
    }
}
"""