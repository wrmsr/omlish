import itertools
import signal
import sys
import time

from omlish.diag.threads import dump_threads_str
import pdb


def handler(signum, frame):
    print(dump_threads_str(), file=sys.stderr)


def _main() -> None:
    signal.signal(signal.SIGQUIT, handler)
    for i in itertools.count():
        print(i)
        time.sleep(1)


if __name__ == '__main__':
    _main()
