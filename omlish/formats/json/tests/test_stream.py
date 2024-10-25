import json
import math

from .... import check
from .... import lang
from ..stream import JsonStreamLexer
from ..stream import JsonStreamValueBuilder
from ..stream import JsonObjectBuilder
from ..stream import yield_parser_events


def assert_json_eq(l, r):
    assert type(l) is type(r)

    if isinstance(l, dict):
        assert set(l) == set(r)
        for k, lv in l.items():
            assert_json_eq(lv, r[k])

    elif isinstance(l, list):
        assert len(l) == len(r)
        for lv, rv in zip(l, r):
            assert_json_eq(lv, rv)

    elif isinstance(l, float):
        if math.isnan(l):
            assert math.isnan(r)
        else:
            assert l == r

    elif isinstance(l, (str, int, bool, type(None))):
        assert l == r

    else:
        raise TypeError(l)


def test_stream():
    # import json
    # import yaml
    # with open('x/llm/openai/api.yaml') as f:
    #     big_obj = yaml.safe_load(f)

    for s in [
        '{"name": "John", "age": 30, "active": true, "scores": [85, 90, 88], "address": null}',
        '{"name": "John", "age": NaN, "score": Infinity, "active": true, "foo": null}',
        '{"name": "John", "age": NaN, "score": Infinity, "loss": -Infinity, "active": true, "foo": null}',
        '{"name": "John", "active": "\\"hi", "foo": null}',
        lang.get_relative_resources('.', globals=globals())['stress.json'].read_text(),
        # json.dumps(big_obj),
        # json.dumps(big_obj, indent=2),
    ]:
        vs = []
        with JsonStreamLexer() as lex:
            with JsonStreamValueBuilder() as vb:
                h = []
                for c in s:
                    for t in lex(c):
                        print(t)
                        h.append(t)
                        for v in vb(t):
                            print(v)
                            vs.append(v)

        print()

        v = check.single(vs)
        x = json.loads(s)
        assert_json_eq(v, x)


def test_parse():
    obj = json.loads(lang.get_relative_resources('.', globals=globals())['stress.json'].read_text())

    with JsonObjectBuilder() as job:
        for e in yield_parser_events(obj):
            for v in job(e):
                print(v)
