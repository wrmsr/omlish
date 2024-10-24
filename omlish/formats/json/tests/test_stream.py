from .... import lang
from ..stream import JsonStreamLexer
from ..stream import JsonStreamValueBuilder


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
        with JsonStreamLexer() as lex:
            with JsonStreamValueBuilder() as vb:
                for c in s:
                    for t in lex(c):
                        print(t)
                        for v in vb(t):
                            print(v)

        print()
