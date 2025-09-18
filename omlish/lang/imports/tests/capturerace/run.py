import functools
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

    def thr_main(arg):
        say('0')
        cl0.count_down()
        say('1')
        ev0.wait()
        say('2')

    a_thr = threading.Thread(name='a', target=functools.partial(thr_main, 'a'))
    b_thr = threading.Thread(name='b', target=functools.partial(thr_main, 'b'))

    a_thr.start()
    b_thr.start()
    cl0.wait()
    ev0.set()
    a_thr.join()
    b_thr.join()


if __name__ == '__main__':
    _main()
