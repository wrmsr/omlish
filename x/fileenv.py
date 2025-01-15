import argparse

import yaml

from omlish import check
from omlish.specs import jmespath


VALUE_TYPES = (
    str,
    int,
    float,
    bool,
)


def _main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('file')
    parser.add_argument('item', nargs='*')

    args = parser.parse_args()

    with open(args.file, 'r') as f:
        obj = yaml.safe_load(f)

    for item in args.item:
        if '=' not in item:
            k = item
            v = obj[k]

        else:
            k, p = item.split('=')
            v = jmespath.search(p, obj)

        check.isinstance(v, VALUE_TYPES)
        print(f'{k}={v}')


if __name__ == '__main__':
    _main()
