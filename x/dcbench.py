"""
import dataclasses as dc0
from omlish import dataclasses as dc1
from x import dataclasses as dc2

dc = dc0
%timeit dc.make_dataclass('C', [('x', int), 'y', ('z', int, dc.field(default=5))], namespace={'add_one': lambda self: self.x + 1})
92 μs ± 1.13 μs per loop (mean ± std. dev. of 7 runs, 10,000 loops each)

dc = dc1
%timeit dc.make_dataclass('C', [('x', int), 'y', ('z', int, dc.field(default=5))], namespace={'add_one': lambda self: self.x + 1})
184 μs ± 705 ns per loop (mean ± std. dev. of 7 runs, 10,000 loops each)

dc = dc2
%timeit dc.make_dataclass('C', [('x', int), 'y', ('z', int, dc.field(default=5))], namespace={'add_one': lambda self: self.x + 1})
244 μs ± 1.1 μs per loop (mean ± std. dev. of 7 runs, 1,000 loops each)
"""
import argparse
import contextlib
import time
import typing as ta



##


@contextlib.contextmanager
def timing_context(n: int):
    st = time.time()

    yield

    et = time.time()

    print(f'Time elapsed: {(et - st) * 1_000_000. / n:.2f} us')


#


@contextlib.contextmanager
def yappi_profiling_context():
    import yappi

    yappi.set_clock_type("cpu")  # Use set_clock_type("wall") for wall time
    yappi.start()

    yield

    fs = yappi.get_func_stats()
    fs.print_all()
    fs.sort('subtime').print_all()


##


def run_class(dc):
    @dc.dataclass()
    class C:  # noqa
        x: int
        y: ta.Any
        z: int = dc.field(default=5)

        def add_one(self):
            return self.x + 1,


def run_make(dc):
    dc.make_dataclass(
        'C',
        [
            ('x', int),
            'y',
            ('z', int, dc.field(default=5)),
        ],
        namespace={
            'add_one': lambda self: self.x + 1,
        },
    )


def _main() -> None:
    default_dc = 1

    parser = argparse.ArgumentParser()
    parser.add_argument('mode', type=int, default=default_dc, nargs='?')
    parser.add_argument('-n', type=int, default=1000)
    parser.add_argument('-m', '--use-make', action='store_true')
    parser.add_argument('-y', '--yappi', action='store_true')
    args = parser.parse_args()

    def dc0():
        import dataclasses as dc
        return dc

    def dc1():
        from omlish import dataclasses as dc
        return dc

    # def dc2():
    #     from x import dataclasses_ as dc
    #     return dc

    modules = [
        dc0,
        dc1,
        # dc2,
    ]

    dc = modules[args.mode]()

    if args.use_make:
        f = run_make
    else:
        f = run_class
    f(dc)

    with contextlib.ExitStack() as es:
        if args.yappi:
            es.enter_context(yappi_profiling_context())

        es.enter_context(timing_context(args.n))

        for _ in range(args.n):
            f(dc)


if __name__ == '__main__':
    _main()
