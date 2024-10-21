"""
TODO:
 - len
 - required character classes
  - lowercase
  - uppercase
  - digits
  - symbols
 - move to omlish/secrets
 - argparse, CliCmd
"""
import argparse
import random
import secrets
import string
import typing as ta


CHAR_CLASSES: ta.Mapping[str, str] = {
    'lower': string.ascii_lowercase,
    'upper': string.ascii_uppercase,
    'digit': string.digits,
    'special': string.punctuation,
}


ALL_CHAR_CLASSES = tuple(CHAR_CLASSES.values())
DEFAULT_LENGTH = 16


def generate_password(
        char_classes: ta.Sequence[str] = ALL_CHAR_CLASSES,
        length: int = DEFAULT_LENGTH,
        *,
        rand: random.Random | None = None,
) -> str:
    if rand is None:
        rand = secrets.SystemRandom()
    l: list[str] = []
    for cc in char_classes:
        l.append(rand.choice(cc))
    cs = ''.join(char_classes)
    if not cs:
        raise ValueError(cs)
    while len(l) < length:
        l.append(rand.choice(cs))
    rand.shuffle(l)
    return ''.join(l)


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('length', type=int, nargs='?', default=DEFAULT_LENGTH)
    for cc in CHAR_CLASSES:
        parser.add_argument(f'-{cc[0]}', f'--{cc}', action='store_true')
    args = parser.parse_args()

    cs = {
        cc
        for cc in CHAR_CLASSES
        if getattr(args, cc) is not None
    }
    if cs:
        ccs = tuple(CHAR_CLASSES[cc] for cc in cs)
    else:
        ccs = ALL_CHAR_CLASSES

    pw = generate_password(
        ccs,
        args.length,
    )
    print(pw)


# @omlish-manifest
_CLI_MODULE = {'$omdev.cli.types.CliModule': {
    'cmd_name': 'pwgen',
    'mod_name': __name__,
}}


if __name__ == '__main__':
    _main()
