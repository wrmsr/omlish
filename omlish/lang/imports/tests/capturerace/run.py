import functools  # noqa
import sys
import threading
import time

from ..... import sync
from ... import capture  # noqa
from ... import proxy  # noqa


def _main() -> None:
    say_lock = threading.Lock()

    st_ns = time.time_ns()

    def say(s):
        with say_lock:
            print(
                f'thr:{threading.current_thread().name} '
                f'tid:{threading.get_native_id():x} '
                f'ns:{time.time_ns() - st_ns:_} '
                f'{s}',
                file=sys.stderr,
            )

    #

    cl0 = sync.CountDownLatch(2)
    ev0 = threading.Event()

    def a_main():
        cl0.count_down()
        ev0.wait()

        say('start')
        from .base import moda  # noqa
        say('end')

    def b_main():
        cl0.count_down()
        ev0.wait()

        say('start')
        from .base import modb  # noqa
        say('end')

    a_thr = threading.Thread(name='a', target=a_main)
    b_thr = threading.Thread(name='b', target=b_main)

    a_thr.start()
    b_thr.start()
    cl0.wait()
    ev0.set()
    a_thr.join()
    b_thr.join()


if __name__ == '__main__':
    _main()
