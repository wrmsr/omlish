import dataclasses as dc
import typing as ta

from omlish import lang
import anyio.abc

from .types import Service
from .types import ServiceId
from .types import UnstoppedServiceReport


class SupervisorMessage(lang.Abstract):
    pass


@dc.dataclass()
class ListServices(SupervisorMessage, lang.Final):
    c: anyio.abc.ObjectReceiveStream[list[Service]]


@dc.dataclass()
class RemoveService(SupervisorMessage, lang.Final):
    sid: ServiceId
    notification: anyio.abc.ObjectReceiveStream[ta.Any]


@dc.dataclass()
class SyncSupervisor(SupervisorMessage, lang.Final):
    pass


# func (s *Supervisor) sync() {
#     select {
#     case s.control <- syncSupervisor{}:
#     case <-s.liveness:

@dc.dataclass()
class ServiceFailed(SupervisorMessage, lang.Final):
    sid: ServiceId
    panic_val: ta.Any
    stacktrace: str


# func (s *Supervisor) fail(sid ServiceId, panicVal interface{}, stacktrace []byte) {
#     select {
#     case s.control <- serviceFailed{sid, panicVal, stacktrace}:
#     case <-s.liveness:

@dc.dataclass()
class ServiceEnded(SupervisorMessage, lang.Final):
    sid: ServiceId
    err: Exception


# func (s *Supervisor) serviceEnded(sid ServiceId, err error) {
#     s.sendControl(serviceEnded{sid, err})

# added by the Add() method
@dc.dataclass()
class AddService(SupervisorMessage, lang.Final):
    service: Service
    name: str
    response: anyio.abc.ObjectReceiveStream[ServiceId]


@dc.dataclass()
class StopSupervisor(SupervisorMessage, lang.Final):
    done: anyio.abc.ObjectReceiveStream[UnstoppedServiceReport]


@dc.dataclass()
class PanicSupervisor(SupervisorMessage, lang.Final):
    pass

# func (s *Supervisor) panic() {
#     s.control <- panicSupervisor{}
