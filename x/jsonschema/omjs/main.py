"""
TODO:
 - jsonpointer


===

https://json-schema.org/specification
https://json-schema.org/draft/2020-12/json-schema-validation
https://datatracker.ietf.org/doc/html/draft-bhutton-relative-json-pointer-00

==

{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://json-schema.org/draft/2020-12/meta/core",
    "$dynamicAnchor": "meta",

    "title": "Core vocabulary meta-schema",
    "type": ["object", "boolean"],
    "properties": {
        "$id": {
            "$ref": "#/$defs/uriReferenceString",
            "$comment": "Non-empty fragments not allowed.",
            "pattern": "^[^#]*#?$"
        },
        "$schema": { "$ref": "#/$defs/uriString" },
        "$ref": { "$ref": "#/$defs/uriReferenceString" },
        "$anchor": { "$ref": "#/$defs/anchorString" },
        "$dynamicRef": { "$ref": "#/$defs/uriReferenceString" },
        "$dynamicAnchor": { "$ref": "#/$defs/anchorString" },
        "$vocabulary": {
            "type": "object",
            "propertyNames": { "$ref": "#/$defs/uriString" },
            "additionalProperties": {
                "type": "boolean"
            }
        },
        "$comment": {
            "type": "string"
        },
        "$defs": {
            "type": "object",
            "additionalProperties": { "$dynamicRef": "#meta" }
        }
    },
    "$defs": {
        "anchorString": {
            "type": "string",
            "pattern": "^[A-Za-z_][-A-Za-z0-9._]*$"
        },
        "uriString": {
            "type": "string",
            "format": "uri"
        },
        "uriReferenceString": {
            "type": "string",
            "format": "uri-reference"
        }
    }
}

{
    "$schema": "https://json-schema.org/draft/2020-12/hyper-schema",
    "$id": "https://json-schema.org/draft/2020-12/hyper-schema",
    "$vocabulary": {
        "https://json-schema.org/draft/2020-12/vocab/core": true,
        "https://json-schema.org/draft/2020-12/vocab/applicator": true,
        "https://json-schema.org/draft/2020-12/vocab/unevaluated": true,
        "https://json-schema.org/draft/2020-12/vocab/validation": true,
        "https://json-schema.org/draft/2020-12/vocab/meta-data": true,
        "https://json-schema.org/draft/2020-12/vocab/format-annotation": true,
        "https://json-schema.org/draft/2020-12/vocab/content": true,
        "https://json-schema.org/draft/2019-09/vocab/hyper-schema": true
    },
    "$dynamicAnchor": "meta",

    "title": "JSON Hyper-Schema",
    "allOf": [
        { "$ref": "https://json-schema.org/draft/2020-12/schema" },
        { "$ref": "https://json-schema.org/draft/2020-12/meta/hyper-schema" }
    ],
    "links": [
        {
            "rel": "self",
            "href": "{+%24id}"
        }
    ]
}

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://json-schema.org/draft/2020-12/output/schema",
  "description": "A schema that validates the minimum requirements for validation output",

  "anyOf": [
    { "$ref": "#/$defs/flag" },
    { "$ref": "#/$defs/basic" },
    { "$ref": "#/$defs/detailed" },
    { "$ref": "#/$defs/verbose" }
  ],
  "$defs": {
    "outputUnit":{
      "properties": {
        "valid": { "type": "boolean" },
        "keywordLocation": {
          "type": "string",
          "format": "json-pointer"
        },
        "absoluteKeywordLocation": {
          "type": "string",
          "format": "uri"
        },
        "instanceLocation": {
          "type": "string",
          "format": "json-pointer"
        },
        "error": {
          "type": "string"
        },
        "errors": {
          "$ref": "#/$defs/outputUnitArray"
        },
        "annotations": {
          "$ref": "#/$defs/outputUnitArray"
        }
      },
      "required": [ "valid", "keywordLocation", "instanceLocation" ],
      "allOf": [
        {
          "if": {
            "properties": {
              "valid": { "const": false }
            }
          },
          "then": {
            "anyOf": [
              {
                "required": [ "error" ]
              },
              {
                "required": [ "errors" ]
              }
            ]
          }
        },
        {
          "if": {
            "anyOf": [
              {
                "properties": {
                  "keywordLocation": {
                    "pattern": "/\\$ref/"
                  }
                }
              },
              {
                "properties": {
                  "keywordLocation": {
                    "pattern": "/\\$dynamicRef/"
                  }
                }
              }
            ]
          },
          "then": {
            "required": [ "absoluteKeywordLocation" ]
          }
        }
      ]
    },
    "outputUnitArray": {
      "type": "array",
      "items": { "$ref": "#/$defs/outputUnit" }
    },
    "flag": {
      "properties": {
        "valid": { "type": "boolean" }
      },
      "required": [ "valid" ]
    },
    "basic": { "$ref": "#/$defs/outputUnit" },
    "detailed": { "$ref": "#/$defs/outputUnit" },
    "verbose": { "$ref": "#/$defs/outputUnit" }
  }
}
"""
import abc
import enum
import operator
import typing as ta

from omlish import cached
from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang


CORE_VOCABULARY = {
    '$schema',
    '$id',
}

VALIDATION_VOCABULARY = {
    'type',

    'properties',
    'required',

    'exclusiveMinimum',
}


##


"""
Unrecognized individual keywords simply have their values collected as annotations, while the behavior with respect to
an unrecognized vocabulary can be controlled when declaring which vocabularies are in use.

A JSON Schema MUST be an object or a boolean.

Keyword categories:
 - identifiers: control schema identification through setting a URI for the schema and/or changing how the base URI is
     determined
 - assertions: produce a boolean result when applied to an instance
 - annotations: attach information to an instance for application use
 - applicators: apply one or more subschemas to a particular location in the instance, and combine or modify thei
     results
 - reserved locations: do not directly affect results, but reserve a place for a specific purpose to ensur
     interoperability

A missing keyword MUST NOT produce a false assertion result, MUST NOT produce annotation results, and MUST NOT cause any
other schema to be evaluated as part of its own behavioral definition.

However, even if the value which produces the default behavior would produce annotation results if present, the default
behavior still MUST NOT result in annotations.
"""


"""
While most JSON Schema keywords can be evaluated on their own, or at most need to take into account the values or
results of adjacent keywords in the same schema object, a few have more complex behavior.

The lexical scope of a keyword is determined by the nested JSON data structure of objects and arrays. The largest such
scope is an entire schema document. The smallest scope is a single schema object with no subschemas.

Keywords MAY be defined with a partial value, such as a URI-reference, which must be resolved against another value,
such as another URI-reference or a full URI, which is found through the lexical structure of the JSON document. The
"$id", "$ref", and "$dynamicRef" core keywords, and the "base" JSON Hyper-Schema keyword, are examples of this sort of
behavior.

Note that some keywords, such as "$schema", apply to the lexical scope of the entire schema resource, and therefore MUST
only appear in a schema resource's root schema.

Other keywords may take into account the dynamic scope that exists during the evaluation of a schema, typically together
with an instance document. The outermost dynamic scope is the schema object at which processing begins, even if it is
not a schema resource root. The path from this root schema to any particular keyword (that includes any "$ref" and
"$dynamicRef" keywords that may have been resolved) is considered the keyword's "validation path."

Lexical and dynamic scopes align until a reference keyword is encountered. While following the reference keyword moves
processing from one lexical scope into a different one, from the perspective of dynamic scope, following a reference is
no different from descending into a subschema present as a value. A keyword on the far side of that reference that
resolves information through the dynamic scope will consider the originating side of the reference to be their dynamic
parent, rather than examining the local lexically enclosing parent.

The concept of dynamic scope is primarily used with "$dynamicRef" and "$dynamicAnchor", and should be considered an
advanced feature and used with caution when defining additional keywords. It also appears when reporting errors and
collected annotations, as it may be possible to revisit the same lexical scope repeatedly with different dynamic scopes.
In such cases, it is important to inform the user of the dynamic path that produced the error or annotation.
"""


##


class JsonType(enum.Enum):
    NULL = enum.auto()
    BOOLEAN = enum.auto()
    OBJECT = enum.auto()
    ARRAY = enum.auto()
    NUMBER = enum.auto()
    STRING = enum.auto()


##


# @dc.dataclass(frozen=True, kw_only=True)
# class Schema(lang.Abstract, lang.Sealed):
#     id: str | None = None
#
#
# ##
#
#
# class TypeSchema(lang.Abstract):
#     pass
#
#
# class NullSchema(TypeSchema, lang.Final):
#     pass
#
#
# class BooleanSchema(TypeSchema, lang.Final):
#     pass
#
#
# class ObjectSchema(TypeSchema, lang.Final):
#     pass
#
#
# class ArraySchema(TypeSchema, lang.Final):
#     pass
#
#
# class NumberSchema(TypeSchema, lang.Final):
#     pass
#
#
# class StringSchema(TypeSchema, lang.Final):
#     pass
#
#
# ##
#
#
# @dc.dataclass(frozen=True, kw_only=True)
# class RootSchema(Schema, lang.Final):
#     metaschema: str | None = None
#      type_: TypeSchema | None = None


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


if __name__ == '__main__':
    _main()
