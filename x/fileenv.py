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

        #

        if isinstance(v, str):
            s = v

        elif isinstance(v, bool):
            s = 'true' if v else 'false'

        else:
            check.isinstance(v, VALUE_TYPES)
            s = str(v)

        #

        check.equal(s.strip(), s)
        for c in '\t\n':
            check.not_in(c, s)
        #

        print(f'{k}={s}')


if __name__ == '__main__':
    _main()
