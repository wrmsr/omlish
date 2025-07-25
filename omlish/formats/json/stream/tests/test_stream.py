import json
import typing as ta

import pytest

from ..... import check
from ...tests.helpers import TEST_DOCS
from ...tests.helpers import assert_json_eq
from ..building import JsonValueBuilder
from ..lexing import JsonStreamLexer
from ..parsing import JsonStreamParser
from ..parsing import yield_parser_events
from ..rendering import StreamJsonRenderer
from ..utils import stream_parse_one_value


@pytest.mark.parametrize('include_space', [False, True])
def test_stream(include_space):
    verbose = False

    for i, s in enumerate(TEST_DOCS):  # noqa
        ts = []
        es = []
        vs = []
        with JsonStreamLexer(
                include_space=include_space,
        ) as lex:
            with JsonStreamParser() as parse:
                with JsonValueBuilder() as build:
                    for c in [*s, '']:
                        verbose and print(c)
                        for t in lex(c):
                            verbose and print(t)
                            ts.append(t)
                            for e in parse(t):
                                verbose and print(e)
                                es.append(e)
                                for v in build(e):
                                    vs.append(v)
                                    print(v)

        print()

        v = check.single(vs)
        x = json.loads(s)
        assert_json_eq(v, x)


def test_parse():
    for i, s in enumerate(TEST_DOCS):  # noqa
        obj = json.loads(s)

        vs = []
        with JsonValueBuilder() as jvb:
            for e in yield_parser_events(obj):
                for v in jvb(e):
                    print(v)
                    vs.append(v)

        v = check.single(vs)
        assert_json_eq(v, obj)


def test_delimit():
    s = """"abc""def"{"a":{"b":[]}}[1]"""

    kw: ta.Any
    for kw in [
        dict(delimiter='\n'),
        dict(indent=2, delimiter='\n'),
    ]:
        with JsonStreamLexer() as lex:
            with JsonStreamParser() as parse:
                r = StreamJsonRenderer.render_str((
                    e
                    for c in s
                    for t in lex(c)
                    for e in parse(t)
                ), **kw)

        print(r)


def test_partial():
    oj = '{"name": "multiply", "arguments": {"a": 12234585, "b": 48838483920}}'
    s = f"""\
<tools>
{oj}
</tools>
    """

    i = iter(s)
    while True:
        if next(i) == '\n':
            break

    o = stream_parse_one_value(i)
    assert o == json.loads(oj)

    r = ''.join(i).strip()
    assert r == '</tools>'
