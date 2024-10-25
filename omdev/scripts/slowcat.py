# @omlish-script
import argparse
import contextlib
import os
import random
import sys
import time


DEFAULT_SLEEP_N = 128
DEFAULT_SLEEP_S = .5


def _main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('files', nargs='*')

    parser.add_argument('-b', '--buffer-size', type=int, default=0x4000)

    parser.add_argument('--initial-sleep')

    parser.add_argument('--sleep-n')
    parser.add_argument('--sleep-s')

    args = parser.parse_args()

    #

    if sleep_s_arg := args.sleep_s:
        if '-' in sleep_s_arg:
            raise NotImplementedError
        else:
            sleep_s_min = sleep_s_max = float(sleep_s_arg)
    else:
        sleep_s_min = sleep_s_max = DEFAULT_SLEEP_S

    if sleep_n_arg := args.sleep_n:
        if '-' in sleep_n_arg:
            raise NotImplementedError
        else:
            sleep_n_min = sleep_n_max = int(sleep_n_arg)
    else:
        sleep_n_min = sleep_n_max = DEFAULT_SLEEP_N

    #

    in_files: list
    if args.files:
        in_files = args.files
    else:
        in_files = [sys.stdin.buffer]

    #

    of = sys.stdout.buffer

    #

    def next_sleep() -> int:
        if sleep_n_min != sleep_n_max:
            o = random.randint(sleep_n_min, sleep_n_max)
        else:
            o = sleep_n_min
        return n + o

    def do_sleep() -> None:
        if sleep_s_min != sleep_s_max:
            s = random.uniform(sleep_s_min, sleep_s_max)
        else:
            s = sleep_s_min
        time.sleep(s)

    #

    if args.initial_sleep:
        do_sleep()

    n = 0
    ns = next_sleep()

    for in_file in in_files:
        with contextlib.ExitStack() as es:
            if isinstance(in_file, str):
                fo = es.enter_context(open(in_file, 'rb'))
            else:
                fo = in_file

            fd = fo.fileno()
            while buf := os.read(fd, args.buffer_size):
                p = 0
                while p < len(buf):
                    c = ns - n
                    r = len(buf) - p
                    if r >= c:
                        r = c
                        sleep = True
                    else:
                        sleep = False

                    of.write(buf[p:p + r])
                    of.flush()

                    n += len(buf)
                    p += r
                    if sleep:
                        do_sleep()
                        ns = next_sleep()


if __name__ == '__main__':
    _main()
