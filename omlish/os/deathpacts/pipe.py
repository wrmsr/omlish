"""
TODO:
 - why didn't this just use set_inheritable(wfd, False)?
"""
import os
import typing as ta
import weakref

from ... import check
from ..forkhooks import ForkHook
from ..forkhooks import ProcessOriginTracker
from .base import BaseDeathpact


##


class PipeDeathpact(BaseDeathpact):
    """
    NOTE: Closes write side in children lazily on poll - does not proactively close write sides on fork. This means
          parents which fork children into codepaths unaware of live PipeDeathpacts will leave write sides open in those
          children, potentially leading to zombies (if those children outlast the parent). Use ForkAwarePipeDeathpact to
          handle such cases.
    """

    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._rfd: int | None = None
        self._wfd: int | None = None

        self._process_origin = ProcessOriginTracker()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(rfd={self._rfd}, wfd={self._wfd})'

    @property
    def pass_fd(self) -> int:
        return check.not_none(self._rfd)

    def is_parent(self) -> bool:
        return self._process_origin.is_in_origin_process()

    #

    def __enter__(self) -> ta.Self:
        check.state(self.is_parent())

        check.none(self._rfd)
        check.none(self._wfd)

        self._rfd, self._wfd = os.pipe()

        os.set_blocking(self._rfd, False)

        return self

    def close(self) -> None:
        if self._rfd is not None:
            os.close(self._rfd)
            self._rfd = None

        if self._wfd is not None:
            if self.is_parent():
                os.close(check.not_none(self._wfd))
            self._wfd = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _close_wfd_if_not_parent(self) -> None:
        if self._wfd is not None:
            if not self.is_parent():
                os.close(check.not_none(self._wfd))
            self._wfd = None

    #

    def __getstate__(self):
        return {
            **self.__dict__,
            **dict(
                _wfd=None,
            ),
        }

    def __setstate__(self, state):
        self.__dict__.update(state)

    #

    def should_die(self) -> bool:
        self._close_wfd_if_not_parent()

        try:
            buf = os.read(check.not_none(self._rfd), 1)
        except BlockingIOError:
            return False

        if buf:
            self._print(f'Read data from pipe! This should not happen! Process state corrupt!')
            self.die()

        return True


#


class ForkAwarePipeDeathpact(PipeDeathpact):
    """
    TODO:
     - Despite no correct way to do threads+forks, still audit thread-safety. Is WeakSet threadsafe? Probably not..
    """

    _PARENTS: ta.ClassVar[ta.MutableSet['ForkAwarePipeDeathpact']] = weakref.WeakSet()

    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._ForkHook.install()
        self._PARENTS.add(self)

    class _ForkHook(ForkHook):
        @classmethod
        def _after_fork_in_child(cls) -> None:
            for pdp in ForkAwarePipeDeathpact._PARENTS:
                pdp._close_wfd_if_not_parent()  # noqa
            ForkAwarePipeDeathpact._PARENTS.clear()
