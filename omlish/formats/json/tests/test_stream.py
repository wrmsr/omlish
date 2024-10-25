import json

from .... import check
from ..stream import JsonObjectBuilder
from ..stream import JsonStreamLexer
from ..stream import JsonStreamParser
from ..stream import yield_parser_events
from .helpers import TEST_DOCS
from .helpers import assert_json_eq


def test_stream():
    for i, s in enumerate(TEST_DOCS):  # noqa
        ts = []
        es = []
        vs = []
        with JsonStreamLexer() as lex:
            with JsonStreamParser() as parse:
                with JsonObjectBuilder() as build:
                    for c in [*s, '']:
                        for t in lex(c):
                            ts.append(t)
                            for e in parse(t):
                                es.append(e)
                                for v in build(e):
                                    vs.append(v)
                                    print(v)

        print()

        v = check.single(vs)
        x = json.loads(s)
        assert_json_eq(v, x)


def test_parse():
    for s in TEST_DOCS:
        obj = json.loads(s)

        vs = []
        with JsonObjectBuilder() as job:
            for e in yield_parser_events(obj):
                for v in job(e):
                    print(v)
                    vs.append(v)

        v = check.single(vs)
        assert_json_eq(v, obj)
