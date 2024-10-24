from ..stream import JsonStreamLexer
from ..stream import json_stream_lex


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
        # json.dumps(big_obj),
        # json.dumps(big_obj, indent=2),
    ]:
        for token in json_stream_lex(iter(s)):
            print(token)

        print()

        with JsonStreamLexer() as lex:
            for c in s:
                for t in lex(c):
                    print(t)

        print()

