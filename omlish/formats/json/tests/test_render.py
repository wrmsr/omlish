import json

import pytest

from ..render import JsonRenderer
from ..render import StreamJsonRenderer
from ..stream import yield_parser_events


DOC = """
{
    "string_example": "This is a string",
    "number_example": 12345,
    "float_example": 123.45,
    "boolean_true": true,
    "boolean_false": false,
    "null_example": null,
    "object_example": {
        "nested_string": "This is a nested string",
        "nested_number": 42,
        "nested_array": [1, 2, 3],
        "nested_boolean": false
    },
    "array_example": [
        "First element",
        100,
        true,
        null,
        {
            "object_in_array": "I'm inside an array"
        },
        [1, 2, "nested array"]
    ],
    "complex_object": {
        "nested_object_1": {
            "name": "John",
            "age": 30,
            "married": true,
            "children": ["Alice", "Bob"],
            "address": {
                "street": "123 Main St",
                "city": "Hometown",
                "zip": "12345"
            }
        },
        "nested_object_2": {
            "product": "Laptop",
            "price": 1299.99,
            "available": false,
            "features": ["16GB RAM", "512GB SSD", "Intel i7"]
        }
    }
}
"""


@pytest.mark.parametrize('indent', [None, 2])
@pytest.mark.parametrize('separators', [None, (',', ':'), (', ', ': ')])
@pytest.mark.parametrize('sort_keys', [False, True])
def test_render(
        indent,
        separators,
        sort_keys,
):
    obj = json.loads(DOC)
    kw = dict(
        indent=indent,
        separators=separators,
        sort_keys=sort_keys,
    )
    r = json.dumps(obj, **kw)

    l = JsonRenderer.render_str(obj, **kw)
    assert l == r

    l = StreamJsonRenderer.render_str(yield_parser_events(obj), **kw)
    assert l == r
