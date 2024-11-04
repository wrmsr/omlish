import argparse
import contextlib
import itertools
import json
import re
import sys


"""
parts = [
    '54.244.199.9',
    '-',
    '-',
    '[20/Jul/2024:17:54:01 +0000]',
    '"GET /profile/jenkinsFile HTTP/1.1"',
    '404',
    '555',
    '"-"',
    '"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"',
]

==

remote_addr
-
remote_user
[time_local]
"request"
status
body_bytes_sent
"http_referer"
"http_user_agent"

==


"""


def _main() -> None:
    pat = re.compile(r'(\[[^\]]*\])|("[^"]*")|([^ ]+)')

    cols = [
        'remote_addr',
        '-',
        'remote_user',
        'time_local',
        'request',
        'status',
        'body_bytes_sent',
        'http_referer',
        'http_user_agent',
    ]

    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')
    args = parser.parse_args()

    with contextlib.ExitStack() as es:
        if args.file:
            f = es.enter_context(open(args.file, 'r'))
        else:
            f = sys.stdin

        for s in f:
            vs = []
            for t in itertools.batched(pat.split(s.strip()), 4):
                if len(t) < 2:
                    continue
                [v] = filter(None, t[1:])
                vs.append(v)
            d = dict(zip(cols, vs, strict=True))


if __name__ == '__main__':
    _main()
