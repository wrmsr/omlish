import argparse
import sys

from ..errors import YamlError
from ..parsing import yaml_parse_str


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
        p = yaml_parse_str(src)
        if isinstance(p, YamlError):
            print(f'ERROR: {p}', file=sys.stderr)
        else:
            print(str(src))


if __name__ == '__main__':
    _main()
