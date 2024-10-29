# ruff: noqa: UP007
import abc
import threading
import typing as ta


class ThreadWorker(abc.ABC):
    def __init__(
            self,
            *,
            stop_event: ta.Optional[threading.Event] = None,
    ) -> None:
        super().__init__()

        if stop_event is None:
            stop_event = threading.Event()
        self._stop_event = stop_event

        self._thread: ta.Optional[threading.Thread] = None

    _sleep_s: float = .5

    def start(self) -> None:
        thr = threading.Thread(target=self._run)
        self._thread = thr
        thr.start()

    @abc.abstractmethod
    def _run(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError

    def cleanup(self) -> None:  # noqa
        pass
