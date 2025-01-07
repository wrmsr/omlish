"""
./python -m gprof2dot -f pstats prof.pstats | dot -Tpdf -o prof.pstats.pdf && open prof.pstats.pdf
"""
import time

from ...dispatch import function


@function
def f(x):
    return 'object'


@f.register
def f_str(x: str):
    return 'str'


def _main():
    f('')

    n = 1_000_000
    start = time.time_ns()

    for _ in range(n):
        f('')

    end = time.time_ns()
    total = end - start
    per = total / n
    print(f'{per} ns / it')


if __name__ == '__main__':
    _main()
