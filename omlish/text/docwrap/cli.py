import argparse

from .api import docwrap
from .rendering import render


##


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('-w', '--width', type=int, default=120)
    parser.add_argument('-i', '--in-place', action='store_true')
    args = parser.parse_args()

    with open(args.file) as f:
        in_txt = f.read()

    root = docwrap(
        in_txt,
        width=args.width,
    )

    out_txt = render(root)

    if args.in_place:
        with open(args.file, 'w') as f:
            f.write(out_txt)
    else:
        print(out_txt)


if __name__ == '__main__':
    _main()
