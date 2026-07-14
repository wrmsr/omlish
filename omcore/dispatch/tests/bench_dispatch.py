import time

from ...dispatch import Dispatcher


def run(**kwargs):
    disp = Dispatcher(**kwargs)
    disp.register('object', [object])
    disp.register('str', [str])
    disp_dispatch = disp.dispatch

    n = 1_000_000
    start = time.time_ns()

    for _ in range(n):
        disp_dispatch(str)

    end = time.time_ns()
    total = end - start
    per = total / n
    print(f'{per} ns / it')


def _main():
    run()
    run(strong_cache=True)


if __name__ == '__main__':
    _main()
