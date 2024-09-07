#!/usr/bin/env python3
# @omlish-lite
# @omlish-script
import argparse
import re
import string


_VERSION_PAT = re.compile(r"__version__ = '(?P<version>[^\']+)'")


def _main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('file')
    parser.add_argument('-w', '--write', action='store_true')
    args = parser.parse_args()

    with open(args.file) as f:
        src = f.read()

    lines = src.splitlines(keepends=True)
    for i, l in enumerate(lines):
        if (m := _VERSION_PAT.fullmatch(l.strip())) is None:
            continue
        parts = m.groupdict()['version'].split('.')
        rp = parts[-1]
        ni = [i for i in range(len(rp)) if rp[i] not in string.digits][-1] + 1
        tp, np = rp[:ni], rp[ni:]
        n = int(np)
        nv = '.'.join([*parts[:-1], tp + str(n + 1)])
        lines[i] = f"__version__ = '{nv}'\n"
    new_src = ''.join(lines)

    if args.write:
        with open(args.file, 'w') as f:
            f.write(new_src)
    else:
        print(new_src)


if __name__ == '__main__':
    _main()
