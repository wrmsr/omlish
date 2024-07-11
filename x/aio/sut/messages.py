import abc
import dataclasses as dc
import enum
import typing as ta

from omlish import lang


class SupervisorMessage(lang.Abstract):
    pass


"""
class ListServices(SupervisorMessage):
    c chan []Service

type removeService struct {
    id           serviceID
    notification chan struct{}
}

##

func (s *Supervisor) sync() {
    select {
    case s.control <- syncSupervisor{}:
    case <-s.liveness:
    }
}

type syncSupervisor struct {
}

##

func (s *Supervisor) fail(id serviceID, panicVal interface{}, stacktrace []byte) {
    select {
    case s.control <- serviceFailed{id, panicVal, stacktrace}:
    case <-s.liveness:
    }
}

type serviceFailed struct {
    id         serviceID
    panicVal   interface{}
    stacktrace []byte
}

##

func (s *Supervisor) serviceEnded(id serviceID, err error) {
    s.sendControl(serviceEnded{id, err})
}

type serviceEnded struct {
    id  serviceID
    err error
}

##

# added by the Add() method
type addService struct {
    service  Service
    name     string
    response chan serviceID
}

##

type stopSupervisor struct {
    done chan UnstoppedServiceReport
}

##

func (s *Supervisor) panic() {
    s.control <- panicSupervisor{}
}

type panicSupervisor struct {
}
"""