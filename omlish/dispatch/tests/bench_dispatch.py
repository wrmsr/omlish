import time

from ...dispatch import Dispatcher


def _main():
    disp = Dispatcher()  # type: ignore
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


if __name__ == '__main__':
    _main()
