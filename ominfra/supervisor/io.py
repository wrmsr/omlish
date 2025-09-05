# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omlish.io.fdio.pollers import FdioPoller
from omlish.logs.modules import get_module_logger

from .dispatchers import Dispatchers
from .types import ExitNow
from .types import HasDispatchers
from .utils.ostypes import Fd


log = get_module_logger(globals())  # noqa


##


HasDispatchersList = ta.NewType('HasDispatchersList', ta.Sequence[HasDispatchers])


class IoManager(HasDispatchers):
    def __init__(
            self,
            *,
            poller: FdioPoller,
            has_dispatchers_list: HasDispatchersList,
    ) -> None:
        super().__init__()

        self._poller = poller
        self._has_dispatchers_list = has_dispatchers_list

    def get_dispatchers(self) -> Dispatchers:
        return Dispatchers(
            d
            for hd in self._has_dispatchers_list
            for d in hd.get_dispatchers()
        )

    def poll(self) -> None:
        dispatchers = self.get_dispatchers()

        self._poller.update(
            {fd for fd, d in dispatchers.items() if d.readable()},
            {fd for fd, d in dispatchers.items() if d.writable()},
        )

        timeout = 1  # this cannot be fewer than the smallest TickEvent (5)

        polled = self._poller.poll(timeout)

        if polled.msg is not None:
            log.error(polled.msg)
        if polled.exc is not None:
            log.error('Poll exception: %r', polled.exc)

        for r in polled.r:
            fd = Fd(r)
            if fd in dispatchers:
                dispatcher = dispatchers[fd]
                try:
                    log.debug('read event caused by %r', dispatcher)
                    dispatcher.on_readable()
                    if not dispatcher.readable():
                        self._poller.unregister_readable(fd)
                except ExitNow:
                    raise
                except Exception as exc:  # noqa
                    log.exception('Error in dispatcher: %r', dispatcher)
                    dispatcher.on_error(exc)
            else:
                # if the fd is not in combined map, we should unregister it. otherwise, it will be polled every
                # time, which may cause 100% cpu usage
                log.debug('unexpected read event from fd %r', fd)
                try:
                    self._poller.unregister_readable(fd)
                except Exception:  # noqa
                    pass

        for w in polled.w:
            fd = Fd(w)
            if fd in dispatchers:
                dispatcher = dispatchers[fd]
                try:
                    log.debug('write event caused by %r', dispatcher)
                    dispatcher.on_writable()
                    if not dispatcher.writable():
                        self._poller.unregister_writable(fd)
                except ExitNow:
                    raise
                except Exception as exc:  # noqa
                    log.exception('Error in dispatcher: %r', dispatcher)
                    dispatcher.on_error(exc)
            else:
                log.debug('unexpected write event from fd %r', fd)
                try:
                    self._poller.unregister_writable(fd)
                except Exception:  # noqa
                    pass
