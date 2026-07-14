# ruff: noqa: UP006 UP007 UP045
import abc
import typing as ta

from omlish.lite.abstract import Abstract

from .utils.users import User


##


SupervisorUser = ta.NewType('SupervisorUser', User)


##


class DaemonizeListener(Abstract):
    def before_daemonize(self) -> None:  # noqa
        pass

    def after_daemonize(self) -> None:  # noqa
        pass


DaemonizeListeners = ta.NewType('DaemonizeListeners', ta.Sequence[DaemonizeListener])


##


class SupervisorSetup(Abstract):
    @abc.abstractmethod
    def setup(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def cleanup(self) -> None:
        raise NotImplementedError
