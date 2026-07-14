import concurrent.futures
import time

from ... import lang
from .. import futures as futs


def test_wait_futures():
    def fn() -> float:
        time.sleep(.2)
        return time.time()

    tp: concurrent.futures.Executor
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as tp:
        futures = [tp.submit(fn) for _ in range(10)]
        assert not futs.wait_futures(futures, tick_fn=iter([True, False]).__next__)
        assert futs.wait_futures(futures)

    def pairs(l):
        return [set(p) for p in lang.chunk(2, l)]

    idxs = [t[0] for t in sorted(enumerate(futures), key=lambda t: t[1].result())]
    assert pairs(idxs) == pairs(range(10))
