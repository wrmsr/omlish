#!/usr/bin/env python3
# @omlish-script
import argparse
import datetime
import json
import os
import re
import sys
import time
import uuid


##


def _main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('n', type=int, default=10, nargs='?')
    parser.add_argument('--message', default='message {i}', nargs='?')
    parser.add_argument('--sleep-s', type=float, nargs='?')
    parser.add_argument('--sleep-n', type=int, nargs='?')

    parser.add_argument('--after-cursor', nargs='?')

    # Ignored
    parser.add_argument('--output', nargs='?')
    parser.add_argument('--follow', action='store_true')
    parser.add_argument('--show-cursor', action='store_true')
    parser.add_argument('--since', nargs='?')

    args = parser.parse_args()

    if (ac := args.after_cursor) is not None:
        if not (m := re.fullmatch(r'cursor:(?P<n>\d+)', ac)):
            raise ValueError(ac)
        start = int(m.groupdict()['n'])
    else:
        start = 0

    stdout_fd = sys.stdout.fileno()
    out_fd = os.dup(stdout_fd)
    null_fd = os.open('/dev/null', os.O_WRONLY)
    os.dup2(null_fd, stdout_fd)

    for i in range(start, args.n):
        if args.sleep_s:
            if not args.sleep_n or (i and i % args.sleep_n == 0):
                time.sleep(args.sleep_s)

        ts_us = datetime.datetime.now(tz=datetime.timezone.utc).timestamp() * 1_000_000  # noqa
        dct = {
            'MESSAGE': args.message.format(i=i),
            'MESSAGE_ID': uuid.uuid4().hex,
            '__CURSOR': f'cursor:{i}',
            '_SOURCE_REALTIME_TIMESTAMP': str(int(ts_us)),
        }

        buf = json.dumps(dct, indent=None, separators=(',', ':')).encode()

        try:
            os.write(out_fd, buf)
            os.write(out_fd, b'\n')
        except BrokenPipeError:
            break


if __name__ == '__main__':
    _main()
