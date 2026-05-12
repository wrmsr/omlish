"""Command-line tool for CBOR diagnostics and testing"""
import argparse
import base64
import contextlib
import datetime
import decimal
import fractions
import functools
import io
import ipaddress
import json
import re
import sys
import typing as ta
import uuid

from .decoder import CborDecoder
from .decoder import cbor_load
from .types import CBOR_UNDEFINED
from .types import CborFrozenDict
from .types import CborSimpleValue
from .types import CborTag


T = ta.TypeVar('T')

JsonValue: ta.TypeAlias = 'str | float | bool | None | list[JsonValue] | dict[str, JsonValue]'


##


DEFAULT_ENCODERS: dict[type, ta.Callable[[ta.Any], ta.Any]] = {  # noqa
    bytes: lambda x: x.decode(encoding='utf-8', errors='backslashreplace'),

    set: list,

    decimal.Decimal: str,
    fractions.Fraction: str,

    datetime.datetime: lambda x: x.isoformat(),
    uuid.UUID: lambda x: x.urn,

    re.compile('').__class__: lambda x: x.pattern,

    ipaddress.IPv4Address: str,
    ipaddress.IPv6Address: str,
    ipaddress.IPv4Network: str,
    ipaddress.IPv6Network: str,

    CborSimpleValue: lambda x: f'cbor_simple:{x.value:d}',
    CborTag: lambda x: {f'CBORTag:{x.tag:d}': x.value},
    CborFrozenDict: lambda x: str(dict(x)),
    type(CBOR_UNDEFINED): lambda x: 'cbor:undef',
}


def tag_hook(decoder: CborDecoder, tag: CborTag, ignore_tags: ta.Collection[int] = ()) -> object:
    if tag.tag in ignore_tags:
        return tag.value

    if tag.tag == 24:
        return decoder.decode_from_bytes(tag.value)
    elif decoder.immutable:
        return f'CBORtag:{tag.tag}:{tag.value}'

    return tag


class DefaultEncoder(json.JSONEncoder):
    def default(self, v: ta.Any) -> ta.Any:
        obj_type = v.__class__
        encoder = DEFAULT_ENCODERS.get(obj_type)
        if encoder:
            return encoder(v)

        return json.JSONEncoder.default(self, v)


def iterdecode(
    f: ta.BinaryIO,
    tag_hook: ta.Callable[[CborDecoder, CborTag], ta.Any] | None = None,
    object_hook: ta.Callable[[CborDecoder, dict[ta.Any, ta.Any]], ta.Any] | None = None,
    str_errors: ta.Literal['strict', 'error', 'replace'] = 'strict',
) -> ta.Iterator[ta.Any]:
    decoder = CborDecoder(f, tag_hook=tag_hook, object_hook=object_hook, str_errors=str_errors)
    while True:
        try:
            yield decoder.decode()
        except EOFError:
            return


def key_to_str(d: T, dict_ids: set[int] | None = None) -> str | list[ta.Any] | dict[str, ta.Any] | T:
    dict_ids = set(dict_ids or [])
    rval: dict[str, ta.Any] = {}
    if not isinstance(d, dict):
        if isinstance(d, CborSimpleValue):
            return f'cbor_simple:{d.value:d}'

        if isinstance(d, (tuple, list, set)):
            if id(d) in dict_ids:
                raise ValueError('Cannot convert self-referential data to JSON')
            else:
                dict_ids.add(id(d))

            v = [key_to_str(x, dict_ids) for x in d]
            dict_ids.remove(id(d))
            return v
        else:
            return d

    if id(d) in dict_ids:
        raise ValueError('Cannot convert self-referential data to JSON')
    else:
        dict_ids.add(id(d))

    for k, v in d.items():
        if isinstance(k, bytes):
            k = k.decode(encoding='utf-8', errors='backslashreplace')
        elif isinstance(k, CborSimpleValue):
            k = f'cbor_simple:{k.value:d}'
        elif isinstance(k, (CborFrozenDict, frozenset, tuple)):
            k = str(k)

        if isinstance(v, dict):
            rval[k] = key_to_str(v, dict_ids)
        elif isinstance(v, (tuple, list, set)):
            rval[k] = [key_to_str(x, dict_ids) for x in v]
        else:
            rval[k] = v

    return rval


def main() -> None:
    prog = 'python -m cbor2.tool'
    description = (
        'A simple command line interface for cbor2 module '
        'to validate and pretty-print CBOR objects.'
    )
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument('-o', '--outfile', type=str, help='output file', default='-')
    parser.add_argument(
        'infiles',
        nargs='*',
        default=['-'],
        help='Collection of CBOR files to process or - for stdin',
    )
    parser.add_argument(
        '-k',
        '--sort-keys',
        action='store_true',
        default=False,
        help='sort the output of dictionaries alphabetically by key',
    )
    parser.add_argument(
        '-p',
        '--pretty',
        action='store_true',
        default=False,
        help='indent the output to look good',
    )
    parser.add_argument(
        '-s',
        '--sequence',
        action='store_true',
        default=False,
        help='Parse a sequence of concatenated CBOR items',
    )
    parser.add_argument(
        '-d',
        '--decode',
        action='store_true',
        default=False,
        help='CBOR data is base64 encoded (handy for stdin)',
    )
    parser.add_argument(
        '-i',
        '--tag-ignore',
        type=str,
        default='',
        help='Comma separated list of tags to ignore and only return the value',
    )
    options = parser.parse_args()

    if options.outfile == '-':
        outfile = 1
        closefd = False
    else:
        outfile = options.outfile
        closefd = True

    ignore_s = options.tag_ignore.split(',')
    droptags = {int(n) for n in ignore_s if (len(n) and n[0].isdigit())}
    my_hook = functools.partial(tag_hook, ignore_tags=droptags)

    with open(
        outfile, mode='w', encoding='utf-8', errors='backslashreplace', closefd=closefd,
    ) as outfp:
        for path in options.infiles:
            with contextlib.ExitStack() as stack:
                if path == '-':
                    infile: ta.BinaryIO = sys.stdin.buffer
                else:
                    infile = stack.enter_context(open(path, mode='rb'))

                if options.decode:
                    infile = io.BytesIO(base64.b64decode(infile.read()))

                try:
                    if options.sequence:
                        objs: ta.Iterable[ta.Any] = iterdecode(infile, tag_hook=my_hook)
                    else:
                        objs = (cbor_load(infile, tag_hook=my_hook),)

                    for obj in objs:
                        json.dump(
                            key_to_str(obj),
                            outfp,
                            sort_keys=options.sort_keys,
                            indent=(None, 4)[options.pretty],
                            cls=DefaultEncoder,
                            ensure_ascii=False,
                        )
                        outfp.write('\n')
                except (ValueError, EOFError) as e:  # pragma: no cover
                    raise SystemExit(e)


if __name__ == '__main__':  # pragma: no cover
    main()
