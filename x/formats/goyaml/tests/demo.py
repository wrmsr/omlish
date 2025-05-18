import argparse
import sys

from ..parsing import parse_str


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='*')
    args = parser.parse_args()

    srcs: list[str] = []
    if not args.files:
        srcs.append(sys.stdin.read())
    else:
        for fp in args.files:
            with open(fp) as f:
                srcs.append(f.read())

    for src in srcs:
        p, err = parse_str(src)
        if err is not None:
            print(f'ERROR: {err}', file=sys.stderr)
        else:
            print(str(src))


if __name__ == '__main__':
    _main()
