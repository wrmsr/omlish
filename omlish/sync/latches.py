# ruff: noqa: UP006 UP043 UP045
# @omlish-lite
import threading
import typing as ta


##


class CountDownLatch:
    def __init__(self, count: int) -> None:
        super().__init__()

        self._count = count
        self._cond = threading.Condition()

    def count_down(self) -> None:
        with self._cond:
            self._count -= 1
            if self._count <= 0:
                self._cond.notify_all()

    def wait(
            self,
            timeout: ta.Optional[float] = None,
    ) -> bool:
        with self._cond:
            return self._cond.wait_for(
                lambda: self._count < 1,
                timeout,
            )
