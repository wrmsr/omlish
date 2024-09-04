"""
TODO:
 - multi
"""
import time
import typing as ta


T = ta.TypeVar('T')


class ProgressReporter(ta.Generic[T]):
    def __init__(
            self,
            *,
            fn: ta.Callable[[], T] | None = None,
            start: T | None = None,

            fmt: str | None = None,
            suffix: str | None = None,
            total: T | None = None,
            report_interval: T | None = None,
    ) -> None:
        super().__init__()

        if fn is not None and start is None:
            self._fn = fn
            start = fn()
        elif start is not None and fn is None:
            self._fn = None
        else:
            raise Exception('Must specify either fn or start')

        self._fmt = fmt
        self._suffix = suffix
        self._total_v = total
        self._report_interval_v = report_interval

        self._cur_v = start
        self._start_v = self._cur_v
        self._start_t = time.time()
        self._reported_v: T | None = None
        self._reported_t: float | None = None

    def update(self, cur: T | None = None) -> T:
        if self._fn is not None:
            if cur is not None:
                raise Exception('Must not specify cur when fn given')
            cur = self._fn()
        else:  # noqa
            if cur is None:
                raise Exception('Must specify cur when fn not given')
        self._cur_v = cur
        return cur

    class Progress(ta.NamedTuple, ta.Generic[T]):
        cur_v: T
        report_base_v: T
        report_elapsed_v: T

        cur_t: float
        report_base_t: float
        report_elapsed_t: float

    def progress(self) -> Progress[T]:
        return ProgressReporter.Progress(
            cur_v=(cur_v := self._cur_v),
            report_base_v=(base_v := self._reported_v if self._reported_v is not None else self._start_v),
            report_elapsed_v=cur_v - base_v,

            cur_t=(cur_t := time.time()),
            report_base_t=(base_t := self._reported_t if self._reported_t is not None else self._start_t),
            report_elapsed_t=cur_t - base_t,
        )

    @property
    def should_report(self) -> bool:
        if self._report_interval_v is None:
            return False
        return self.progress().report_elapsed_v >= self._report_interval_v

    def report(self) -> list[str]:
        prg = self.progress()

        def fmt_v(v: T) -> str:
            if self._fmt is None:
                return str(v)
            return f'{{:{self._fmt}}}'.format(v)  # noqa

        ps = []
        sfx = ' ' + self._suffix if self._suffix is not None else ''
        if self._total_v is not None:
            ps.extend([
                f'{fmt_v(prg.cur_v)} / {fmt_v(self._total_v)}' + sfx,
                f'{prg.cur_v / self._total_v * 100.:.02f} %',
            ])
        else:
            ps.append(f'{fmt_v(self._cur_v)}' + sfx)
        ps.append(
            f'{fmt_v(type(prg.cur_v)(prg.report_elapsed_v / prg.report_elapsed_t))} '
            f'{self._suffix if self._suffix is not None else ""}/s',
        )

        self._reported_v = prg.cur_v
        self._reported_t = prg.cur_t

        return ps
