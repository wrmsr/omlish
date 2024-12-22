import sys
import time
import typing as ta


T = ta.TypeVar('T')


##


class ProgressBar:
    """
    TODO:
     - ProgressBarRenderer
     - right-justify
     - ProgressBarGroup
     - animate
    """

    def __init__(
            self,
            total: int | None = None,
            *,
            length: int = 40,
            interval: float = .2,
            start_time: float | None = None,
            out: ta.TextIO | None = None,
    ) -> None:
        super().__init__()

        self._total = total
        self._length = length
        self._interval = interval
        if start_time is None:
            start_time = time.time()
        self._start_time = start_time
        if out is None:
            out = sys.stdout
        self._out = out

        self._i = 0
        self._elapsed = 0.
        self._last_print = 0.

    def render(
            self,
            *,
            complete: bool = False,
    ) -> str:
        iter_per_sec = self._i / self._elapsed if self._elapsed > 0 else 0

        if self._total is not None:
            remaining = (self._total - self._i) / iter_per_sec if iter_per_sec > 0 else 0
            done = int(self._length * self._i / self._total)

            bar = f'[{"█" * done}{"." * (self._length - done)}]'
            info_parts = [
                f'{self._i}/{self._total}',
                f'{iter_per_sec:.2f} it/s',
                f'{self._elapsed:.2f}s elapsed',
                f'{remaining:.2f}s left',
            ]

        else:
            bar = f'[{("█" if complete else "?") * self._length}]'
            info_parts = [
                f'{self._i}',
                f'{iter_per_sec:.2f} it/s',
                f'{self._elapsed:.2f}s elapsed',
            ]

        info = ' | '.join(info_parts)
        return f'{bar} {info}'

    def print(
            self,
            *,
            now: float | None = None,
            **kwargs: ta.Any,
    ) -> None:
        if now is None:
            now = time.time()

        line = self.render(**kwargs)
        self._out.write(f'\033[2K\033[G{line}')
        self._out.flush()

        self._last_print = now

    def update(
            self,
            n: int = 1,
            *,
            now: float | None = None,
            silent: bool = False,
    ) -> None:
        if now is None:
            now = time.time()

        self._i += n
        self._elapsed = now - self._start_time

        if not silent:
            if now - self._last_print >= self._interval:
                self.print(now=now)


def progress_bar(
        seq: ta.Iterable[T],
        *,
        no_tty_check: bool = False,
        total: int | None = None,
        out: ta.TextIO | None = None,
        **kwargs: ta.Any,
) -> ta.Generator[T, None, None]:
    if out is None:
        out = sys.stdout

    if not no_tty_check and not out.isatty():
        yield from seq
        return

    if total is None:
        if isinstance(seq, ta.Sized):
            total = len(seq)

    pb = ProgressBar(
        total=total,
        out=out,
        **kwargs,
    )

    for item in seq:
        pb.update()
        yield item

    pb.print(complete=True)
    out.write('\n')
