# ruff: noqa: UP006 UP007
import abc
import typing as ta

from .users import User


##


SupervisorUser = ta.NewType('SupervisorUser', User)


##


class DaemonizeListener(abc.ABC):
    def before_daemonize(self) -> None:
        pass

    def after_daemonize(self) -> None:
        pass


DaemonizeListeners = ta.NewType('DaemonizeListeners', ta.Sequence[DaemonizeListener])


##


class SupervisorSetup(abc.ABC):
    @abc.abstractmethod
    def setup(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def cleanup(self) -> None:
        raise NotImplementedError
