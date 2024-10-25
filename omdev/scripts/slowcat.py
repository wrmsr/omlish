#!/usr/bin/env python3
# @omlish-script
import argparse
import contextlib
import os
import random
import sys
import time
import typing as ta


T = ta.TypeVar('T')


DEFAULT_SLEEP_N = 128
DEFAULT_SLEEP_S = .5


def _main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('files', nargs='*')

    parser.add_argument('-b', '--buffer-size', type=int, default=0x4000)

    parser.add_argument('-i', '--initial-sleep')

    parser.add_argument('-n', '--sleep-n')
    parser.add_argument('-s', '--sleep-s')

    args = parser.parse_args()

    #

    def parse_range(s: str, d: T) -> tuple[T, T]:
        if not s:
            return d, d
        elif '-' in s:
            l, r = map(type(d), s.split('-'))
            return l, r
        else:
            l = r = type(d)(s)  # type: ignore
            return l, r

    sleep_s_min, sleep_s_max = parse_range(args.sleep_s, DEFAULT_SLEEP_S)
    sleep_n_min, sleep_n_max = parse_range(args.sleep_n, DEFAULT_SLEEP_N)

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


# @omlish-manifest
_CLI_MODULE = {'$omdev.cli.types.CliModule': {
    'cmd_name': 'slowcat',
    'mod_name': __name__,
}}


if __name__ == '__main__':
    _main()
