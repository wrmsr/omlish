"""
TODO:
 - jsonpointer


===

https://json-schema.org/specification
https://json-schema.org/draft/2020-12/json-schema-validation
https://datatracker.ietf.org/doc/html/draft-bhutton-relative-json-pointer-00

"""
import typing as ta

from omlish import check
from omlish import collections as col

from .keywords import KEYWORD_TYPES_BY_TAG
from .keywords import Keyword
from .keywords import Keywords
from .keywords import StrKeyword
from .keywords import StrOrStrsKeyword


KeywordT = ta.TypeVar('KeywordT', bound=Keyword)


##


def build_keyword(cls: type[KeywordT], v: ta.Any) -> KeywordT:
    if issubclass(cls, StrKeyword):
        return cls(check.isinstance(v, str))

    if issubclass(cls, StrOrStrsKeyword):
        ss: str | ta.Sequence[str]
        if isinstance(v, str):
            ss = v
        elif isinstance(v, ta.Iterable):
            ss = col.seq_of(check.of_isinstance(str))(v)
        else:
            raise TypeError(v)
        return cls(ss)

    raise TypeError(cls)


def build_keywords(dct: ta.Mapping[str, ta.Any]) -> Keywords:
    lst: list[Keyword] = []
    for k, v in dct.items():
        cls = KEYWORD_TYPES_BY_TAG[k]
        lst.append(build_keyword(cls, v))
    return Keywords(lst)


##


def _main() -> None:
    # https://json-schema.org/learn/getting-started-step-by-step

    product = {
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

    build_keywords(product_schema)


if __name__ == '__main__':
    _main()
