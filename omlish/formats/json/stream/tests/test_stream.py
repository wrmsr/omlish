import json

from ..... import check
from ...tests.helpers import TEST_DOCS
from ...tests.helpers import assert_json_eq
from ..build import JsonObjectBuilder
from ..lex import JsonStreamLexer
from ..parse import JsonStreamParser
from ..parse import yield_parser_events
from ..render import StreamJsonRenderer


def test_stream():
    verbose = False

    for i, s in enumerate(TEST_DOCS):  # noqa
        ts = []
        es = []
        vs = []
        with JsonStreamLexer() as lex:
            with JsonStreamParser() as parse:
                with JsonObjectBuilder() as build:
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
        with JsonObjectBuilder() as job:
            for e in yield_parser_events(obj):
                for v in job(e):
                    print(v)
                    vs.append(v)

        v = check.single(vs)
        assert_json_eq(v, obj)


def test_delimit():
    s = """"abc""def"{"a":{"b":[]}}[1]"""

    with JsonStreamLexer() as lex:
        with JsonStreamParser() as parse:
            r = StreamJsonRenderer.render_str((
                e
                for c in s
                for t in lex(c)
                for e in parse(t)
            ), delimit='\n')

    print(r)
