"""
./python -m gprof2dot -f pstats prof.pstats | dot -Tpdf -o prof.pstats.pdf && open prof.pstats.pdf
"""
from ..methods import method


class C:
    @method
    def f(self, x):
        return 'object'


class D(C):
    @C.f.register
    def f_str(self, x: str):
        return 'str'


def _main():
    d = D()
    d.f('')

    for _ in range(1_000_000):
        d.f('')


if __name__ == '__main__':
    _main()
