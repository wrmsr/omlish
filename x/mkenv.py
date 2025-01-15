"""
TODO:
 - detect file extension
 - quote values / handle newlines and such

==

export $(./python mkenv.py secrets.yml foo_access_token | xargs)
eval $(om mkenv -e secrets.yml foo_access_token)
"""
import argparse
import json
import sys
import typing as ta

from omlish import check
from omlish import lang
from omlish.specs import jmespath


if ta.TYPE_CHECKING:
    import yaml
else:
    yaml = lang.proxy_import('yaml')


##


VALUE_TYPES = (
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
    parser.add_argument('-e', '--eval', action='store_true')
    parser.add_argument('-u', '--uppercase', action='store_true')
    parser.add_argument('item', nargs='*')

    args = parser.parse_args()

    #

    if args.file == '-':
        obj = json.loads(sys.stdin.read())

    else:
        with open(args.file, 'r') as f:
            obj = yaml.safe_load(f)

    #

    items = extract_items(
        obj,
        args.item,
        uppercase_keys=args.uppercase,
    )

    #

    if args.eval:
        cmd = ' '.join([
            'export',
            *[f'{k}={v}' for k, v in items.items()],
        ])
        print(cmd)

    else:
        for k, v in items.items():
            print(f'{k}={v}')


# @omlish-manifest
_CLI_MODULE = {'$omdev.cli.types.CliModule': {
    'cmd_name': ['mkenv'],
    'mod_name': __name__,
}}


if __name__ == '__main__':
    _main()
