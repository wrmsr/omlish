import os.path
import typing as ta

import pytest

from ...build import JsonObjectBuilder
from ...lex import JsonStreamLexer
from ...parse import JsonStreamParser


##


def parse(
        src: str,
        *,
        verbose: bool = False,
) -> list:
    ts = []
    es = []
    vs = []

    with JsonStreamLexer() as lex:
        with JsonStreamParser() as parse:
            with JsonObjectBuilder() as build:
                for c in [*src, '']:
                    verbose and print(c)
                    for t in lex(c):
                        verbose and print(t)
                        ts.append(t)
                        for e in parse(t):
                            verbose and print(e)
                            es.append(e)
                            for v in build(e):
                                vs.append(v)
                                verbose and print(v)

    return vs


##


Expectation: ta.TypeAlias = ta.Literal[
    'accept',
    'reject',
    'either',
]


EXPECTATION_MAP: ta.Mapping[str, Expectation] = {
    'y': 'accept',
    'n': 'reject',
    'i': 'either',
}


@pytest.mark.xfail(reason='fixme')
def test_suite():
    fails = []

    d = os.path.join(os.path.dirname(__file__), 'parsing')
    for n in sorted(os.listdir(d)):
        with open(os.path.join(d, n), 'rb') as f:
            b = f.read()

        try:
            s = b.decode('utf-8')
        except UnicodeDecodeError:
            continue

        x = EXPECTATION_MAP[n[0]]

        v: ta.Any
        try:
            v = parse(s)
        except Exception as e:  # noqa
            v = e

        if (
            (x == 'accept' and not isinstance(v, Exception)) or
            (x == 'reject' and isinstance(v, Exception)) or
            x == 'either'
        ):
            continue

        fails.append(n)

        print(f'{f=}')
        print(f'{x=}')
        print(f'{v=}')
        print()

    assert len(fails) == 0
