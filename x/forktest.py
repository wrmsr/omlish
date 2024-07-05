import itertools
import os
import time
import sys


def _main():
    if not os.fork():
        for i in itertools.count():
            print(f'child {os.getpid()=} {i=}')
            time.sleep(1)
        raise Exception

    input()
    os.execl(sys.executable, sys.executable, __file__)


if __name__ == '__main__':
    _main()
