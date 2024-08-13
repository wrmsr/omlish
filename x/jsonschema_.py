"""
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
"""

def _main() -> None:
    # https://json-schema.org/learn/getting-started-step-by-step

    product = {
        "productId": 1,
        "productName": "A green door",
        "price": 12.50,
        "tags": ["home", "green"],
    }

    schema_id_root = 'https://github.com/wrmsr/omlish/jsonschemas/'

    product_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": schema_id_root + "product.schema.json",
        "title": "Product",
        "description": "A product in the catalog",
        "type": "object",
        "properties": {
            "productId": {
                "description": "The unique identifier for a product",
                "type": "integer",
            },
            "productName": {
                "description": "Name of the product",
                "type": "string",
            },
            "price": {
                "description": "The price of the product",
                "type": "number",
                "exclusiveMinimum": 0,
            },
        },
        "required": [
            "productId",
            "productName",
            "price",
        ],
    }


if __name__ == '__main__':
    _main()
