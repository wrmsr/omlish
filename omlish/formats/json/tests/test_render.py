import json

from ..render import JsonRenderer


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


def test_render():
    obj = json.loads(DOC)

    kw = {}
    l = JsonRenderer.render_str(obj, **kw)
    r = json.dumps(obj, **kw)
    assert l == r
