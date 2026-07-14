# ruff: noqa: UP006 UP043 UP045
# @om-lite
import threading
import typing as ta


##


class CountDownLatch:
    def __init__(self, count: int) -> None:
        super().__init__()

        self._count = count
        self._cond = threading.Condition()

    def get_count(self) -> int:
        with self._cond:
            return self._count

    def count_down(self) -> None:
        with self._cond:
            if self._count < 1:
                return
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
