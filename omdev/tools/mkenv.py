"""
TODO:
 - detect file extension

==

export $(./python mkenv.py secrets.yml foo_access_token | xargs)
eval $(om mkenv -e secrets.yml foo_access_token)
"""
import argparse
import json
import shlex
import sys
import typing as ta

from omlish import check
from omlish.configs.formats import DEFAULT_CONFIG_FILE_LOADER
from omlish.specs import jmespath


##


VALUE_TYPES: tuple[type, ...] = (
    str,
    int,
    float,
    bool,
)


def extract_item(
        obj: ta.Any,
        item: str,
        *,
        uppercase_keys: bool = False,
) -> tuple[str, str]:
    if '=' not in item:
        k = item
        v = obj[k]
        if uppercase_keys:
            k = k.upper()

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

    return (k, s)


def extract_items(
        obj: ta.Any,
        items: ta.Iterable[str],
        **kwargs: ta.Any,
) -> dict[str, str]:
    return dict(
        extract_item(obj, item, **kwargs)
        for item in items
    )


def _main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('file')
    parser.add_argument('-e', '--for-eval', action='store_true')
    parser.add_argument('-u', '--uppercase', action='store_true')
    parser.add_argument('item', nargs='*')

    args = parser.parse_args()

    #

    if args.file == '-':
        obj = json.loads(sys.stdin.read())

    else:
        data = DEFAULT_CONFIG_FILE_LOADER.load_file(args.file)
        obj = data.as_map()

    #

    items = extract_items(
        obj,
        args.item,
        uppercase_keys=args.uppercase,
    )

    #

    if args.for_eval:
        cmd = ' '.join([
            'export',
            *[f'{k}={qv if (qv := shlex.quote(v)) != v else v}' for k, v in items.items()],
        ])
        print(cmd)

    else:
        for k, v in items.items():
            print(f'{k}={v}')


# @omlish-manifest
_CLI_MODULE = {'!.cli.types.CliModule': {
    'name': ['mkenv'],
    'module': __name__,
}}


if __name__ == '__main__':
    _main()
