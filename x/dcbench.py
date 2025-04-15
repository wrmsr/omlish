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
import sys
import time

import dataclasses as dc0
from omlish import dataclasses as dc1

from . import dataclasses as dc2


def _main() -> None:
    [arg] = sys.argv[1:]
    
    modules = [
        dc0,
        dc1,
        dc2,
    ]
    
    dc = modules[int(arg)]
    
    def f():
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
    
    n = 1_000
    st = time.time()
    for _ in range(1_000):
        f()
    et = time.time()
    
    print(f'Time elapsed: {(et - st) * 1_000_000. / n:.2f} us')


if __name__ == '__main__':
    _main()
    