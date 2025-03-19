"""
TODO:
 - jsonpointer

===

https://json-schema.org/specification
https://json-schema.org/draft/2020-12/json-schema-validation
https://datatracker.ietf.org/doc/html/draft-bhutton-relative-json-pointer-00
"""
from ....formats import json
from ..keywords.parse import parse_keywords
from ..keywords.render import render_keywords


def test_keywords():
    # https://json-schema.org/learn/getting-started-step-by-step

    product = {  # noqa
        'productId': 1,
        'productName': 'A green door',
        'price': 12.50,
        'tags': ['home', 'green'],
    }

    schema_id_root = 'https://github.com/wrmsr/omlish/jsonschemas/'

    warehouse_location_schema = {
        '$id': schema_id_root + 'geographical-location.schema.json',
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        'title': 'Longitude and Latitude',
        'description': 'A geographical coordinate on a planet (most commonly Earth).',
        'type': 'object',
        'required': ['latitude', 'longitude'],
        'properties': {
            'latitude': {
                'type': 'number',
                'minimum': -90,
                'maximum': 90,
            },
            'longitude': {
                'type': 'number',
                'minimum': -180,
                'maximum': 180,
            },
        },
    }

    product_schema = {
        '$id': schema_id_root + 'product.schema.json',
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        'title': 'Product',
        'description': 'A product in the catalog',
        'type': 'object',
        'properties': {
            'productId': {
                'description': 'The unique identifier for a product',
                'type': 'integer',
            },
            'productName': {
                'description': 'Name of the product',
                'type': 'string',
            },
            'price': {
                'description': 'The price of the product',
                'type': 'number',
                'exclusiveMinimum': 0,
            },
            'tags': {
                'description': 'Tags for the product',
                'type': 'array',
                'items': {
                    'type': 'string',
                },
                'minItems': 1,
                'uniqueItems': True,
            },
            'dimensions': {
                'type': 'object',
                'properties': {
                    'length': {
                        'type': 'number',
                    },
                    'width': {
                        'type': 'number',
                    },
                    'height': {
                        'type': 'number',
                    },
                },
                'required': ['length', 'width', 'height'],
            },
            'warehouseLocation': {
                'description': 'Coordinates of the warehouse where the product is located.',
                '$ref': schema_id_root + 'geographical-location.schema.json',
            },
        },
        'required': [
            'productId',
            'productName',
            'price',
        ],
    }

    for schema in [
        warehouse_location_schema,
        product_schema,
    ]:
        kws = parse_keywords(schema)
        print(kws)

        print(json.dumps_pretty(render_keywords(kws)))
