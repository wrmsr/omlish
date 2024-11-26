# ruff: noqa: UP006 UP007
import abc
import typing as ta

from .utils.users import User


##


SupervisorUser = ta.NewType('SupervisorUser', User)


##


class DaemonizeListener(abc.ABC):  # noqa
    def before_daemonize(self) -> None:  # noqa
        pass

    def after_daemonize(self) -> None:  # noqa
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
