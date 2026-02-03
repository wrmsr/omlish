"""
./python -m gprof2dot -f pstats prof.pstats | dot -Tpdf -o prof.pstats.pdf && open prof.pstats.pdf
"""
import time

from ...dispatch import method


def run(**kwargs):
    class C:
        @method(**kwargs)
        def f(self, x):
            return 'object'

    class D(C):
        @C.f.register
        def f_str(self, x: str):
            return 'str'

    d = D()
    d.f('')

    n = 1_000_000
    start = time.time_ns()

    for _ in range(n):
        d.f('')

    end = time.time_ns()
    total = end - start
    per = total / n
    print(f'{per} ns / it')


def _main():
    run()
    run(instance_cache=True)


if __name__ == '__main__':
    _main()
