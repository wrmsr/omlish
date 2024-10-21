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


def generate_password(
        char_classes: ta.Sequence[str],
        length: int = 12,
        *,
        rand: random.Random | None = None,
) -> str:
    if rand is None:
        rand = secrets.SystemRandom()
    l: list[str] = []
    for cc in char_classes:
        l.append(rand.choice(cc))
    cs = ''.join(char_classes)
    while len(l) < length:
        l.append(rand.choice(cs))
    rand.shuffle(l)
    return ''.join(l)


def _main() -> None:
    print(generate_password(list(CHAR_CLASSES.values())))


if __name__ == '__main__':
    _main()
