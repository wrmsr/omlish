"""
'54.244.199.9',
'-',
'-',
'[20/Jul/2024:17:54:01 +0000]',
'"GET /profile/jenkinsFile HTTP/1.1"',
'404',
'555',
'"-"',
'"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"',

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
"""  # noqa
import itertools
import json
import re
import typing as ta


NGINX_LOG_PAT = re.compile(r'(\[[^\]]*\])|("[^"]*")|([^ ]+)')

NGINX_LOG_COLUMNS: ta.Sequence[str] = [
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


def parse_nginx_log_line(
        line: str,
        *,
        columns: ta.Sequence[str] = NGINX_LOG_COLUMNS,
        pattern: re.Pattern = NGINX_LOG_PAT,
        num_groups: int = 4,
) -> dict[str, ta.Any]:
    if isinstance(columns, str):
        raise TypeError(columns)

    vs = []
    for t in itertools.batched(pattern.split(line.strip()), num_groups):
        if len(t) < 2:
            continue
        [v] = filter(None, t[1:])
        vs.append(v)

    return dict(zip(columns, vs, strict=True))


# @omlish-manifest
_CLI_MODULE = {'$omdev.cli.types.CliModule': {
    'cmd_name': 'nginxlogs',
    'mod_name': __name__,
}}


def _main() -> None:
    import argparse
    import contextlib
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')
    args = parser.parse_args()

    with contextlib.ExitStack() as es:
        f: ta.TextIO
        if args.file:
            f = es.enter_context(open(args.file))
        else:
            f = sys.stdin

        for line in f:
            d = parse_nginx_log_line(line)
            print(json.dumps(d))


if __name__ == '__main__':
    _main()
