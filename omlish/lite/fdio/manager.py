# ruff: noqa: UP006 UP007
import typing as ta

from .handlers import FdIoHandler
from .pollers import FdIoPoller


class FdIoManager:
    def __init__(
            self,
            poller: FdIoPoller,
    ) -> None:
        super().__init__()

        self._poller = poller

        self._handlers: ta.Dict[int, FdIoHandler] = {}  # Preserves insertion order

    def register(self, h: FdIoHandler) -> None:
        if (hid := id(h)) in self._handlers:
            raise KeyError(h)
        self._handlers[hid] = h

    def unregister(self, h: FdIoHandler) -> None:
        del self._handlers[id(h)]

    def poll(self, *, timeout: float = 1.) -> None:
        hs = list(self._handlers.values())

        rd = {h.fd(): h for h in hs if h.readable()}
        wd = {h.fd(): h for h in hs if h.writable()}

        self._poller.update(set(rd), set(wd))

        pr = self._poller.poll(timeout)

        for f in pr.r:
            if not (h := rd[f]).closed:
                h.on_readable()
        for f in pr.w:
            if not (h := wd[f]).closed:
                h.on_writable()

        self._handlers = {id(h): h for h in hs if not h.closed}
