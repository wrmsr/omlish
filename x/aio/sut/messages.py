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
    id: ServiceId
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
    id: ServiceId
    panic_val: ta.Any
    stacktrace: str


# func (s *Supervisor) fail(id ServiceId, panicVal interface{}, stacktrace []byte) {
#     select {
#     case s.control <- serviceFailed{id, panicVal, stacktrace}:
#     case <-s.liveness:

@dc.dataclass()
class ServiceEnded(SupervisorMessage, lang.Final):
    id: ServiceId
    err: Exception


# func (s *Supervisor) serviceEnded(id ServiceId, err error) {
#     s.sendControl(serviceEnded{id, err})

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
