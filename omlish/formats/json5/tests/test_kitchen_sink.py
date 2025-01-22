from .... import lang
from ..parsing import parse


KITCHEN_SINK_STR = lang.get_relative_resources(globals=globals())['kitchen_sink.json5'].read_text()

KITCHEN_SINK_OBJ = {
    'unquoted': 'and you can quote me on that',
    'singleQuotes': 'I can use "double quotes" here',
    'lineBreaks': "Look, Mom! No \\n's!",
    'hexadecimal': 912559,
    'leadingDecimalPoint': 0.8675309,
    'andTrailing': 8675309.0,
    'positiveSign': 1.0,
    'trailingComma': 'in objects',
    'andIn': ['arrays'],
    'backwardsCompatible': 'with JSON',
}


def test_kitchen_sink():
    assert parse(KITCHEN_SINK_STR) == KITCHEN_SINK_OBJ
