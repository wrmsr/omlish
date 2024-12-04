import os.path
import typing as ta

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


def test_suite():
    fails: list[str] = []

    xfail_names = frozenset([
        # May decide to make strict
        'n_array_extra_comma.json',
        'n_array_number_and_comma.json',
        'n_object_trailing_comma.json',

        # Special numbers are explicitly supported
        'n_number_NaN.json',
        'n_number_infinity.json',
        'n_number_minus_infinity.json',

        # Supported because streaming
        'n_single_space.json',
        'n_structure_whitespace_formfeed.json',
        'n_structure_no_data.json',
        'n_structure_double_array.json',

        # FIXME:
        'n_structure_object_with_trailing_garbage.json',
    ])

    only_names: frozenset[str] = frozenset([

    ])

    d = os.path.join(os.path.dirname(__file__), 'parsing')
    for n in sorted(os.listdir(d)):
        if only_names and n not in only_names:
            continue

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
            if n in xfail_names:
                raise Exception(f'Expected failure did not fail: {n}')
            continue

        if n in xfail_names:
            continue

        if not fails:
            print()
        print(n)

        # print(f'{x=}')
        # print(f'{v=}')
        # print()

        fails.append(n)

    assert len(fails) == 0
