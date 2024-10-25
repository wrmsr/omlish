"""
# import json
# import yaml
# with open('x/llm/openai/api.yaml') as f:
#     big_obj = yaml.safe_load(f)
"""
import math

from .... import lang


##


SIMPLE_DOCS = [
    'null',

    '1',
    '1.2',

    '"a"',

    '[]',
    '[1]',
    '[1, 2]',

    '{}',
    '{"a": 1}',
    '{"a": 1, "b": 2}',

    '{"a": {"b": [{"c": 1}, [{"d": 2}]]}}',
]

OBJECT_DOCS = [
    '{"name": "John", "age": 30, "active": true, "scores": [85, 90, 88], "address": null}',
    '{"name": "John", "age": NaN, "score": Infinity, "active": true, "foo": null}',
    '{"name": "John", "age": NaN, "score": Infinity, "loss": -Infinity, "active": true, "foo": null}',
    '{"name": "John", "active": "\\"hi", "foo": null, "empty_array": [], "empty_object": {}, "aaa": 2}',
]

STRESS_DOC = lang.get_relative_resources('.', globals=globals())['stress.json'].read_text()

TEST_DOCS = [
    *SIMPLE_DOCS,
    *OBJECT_DOCS,
    STRESS_DOC,
]


##


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
