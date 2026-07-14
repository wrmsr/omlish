"""
jsonschema_features.py

Count JSON Schema feature/keyword usage in a schema document.

Usage:

    python jsonschema_features.py schema.json
    python jsonschema_features.py schema1.json schema2.json
    cat schema.json | python jsonschema_features.py
    python jsonschema_features.py --json schema.json

This is intentionally not a validator or full JSON Schema implementation. It performs a schema-aware traversal
sufficient to distinguish:

    {
      "type": "object",
      "properties": {
        "oneOf": {"type": "string"}
      }
    }

from:

    {
      "oneOf": [
        {"type": "string"},
        {"type": "number"}
      ]
    }
"""
import argparse
import collections
import json
import sys
import typing as ta


##


# Broad union of common JSON Schema draft-04 through 2020-12 keywords, plus a few OpenAPI-adjacent schema keywords that
# show up in the wild.
KNOWN_KEYWORDS = frozenset({
    # Core / identification / refs
    '$schema',
    '$id',
    'id',
    '$anchor',
    '$dynamicAnchor',
    '$ref',
    '$dynamicRef',
    '$defs',
    'definitions',
    '$vocabulary',
    '$comment',

    # Applicator keywords
    'allOf',
    'anyOf',
    'oneOf',
    'not',
    'if',
    'then',
    'else',
    'items',
    'additionalItems',
    'prefixItems',
    'contains',
    'properties',
    'patternProperties',
    'additionalProperties',
    'propertyNames',
    'unevaluatedItems',
    'unevaluatedProperties',
    'dependentSchemas',
    'dependencies',

    # Validation keywords
    'type',
    'enum',
    'const',
    'multipleOf',
    'maximum',
    'exclusiveMaximum',
    'minimum',
    'exclusiveMinimum',
    'maxLength',
    'minLength',
    'pattern',
    'maxItems',
    'minItems',
    'uniqueItems',
    'maxContains',
    'minContains',
    'maxProperties',
    'minProperties',
    'required',
    'dependentRequired',

    # Annotation-ish keywords
    'title',
    'description',
    'default',
    'deprecated',
    'readOnly',
    'writeOnly',
    'examples',

    # String/media/content keywords
    'format',
    'contentEncoding',
    'contentMediaType',
    'contentSchema',

    # OpenAPI-ish common extensions to JSON Schema-ish schemas
    'nullable',
    'discriminator',
    'xml',
    'externalDocs',
    'example',
})


# Keyword value is itself a schema.
SCHEMA_VALUE_KEYWORDS = frozenset({
    'not',
    'if',
    'then',
    'else',
    'contains',
    'additionalProperties',
    'propertyNames',
    'unevaluatedItems',
    'unevaluatedProperties',
    'contentSchema',
    'additionalItems',
})


# Keyword value is a list of schemas.
SCHEMA_ARRAY_KEYWORDS = frozenset({
    'allOf',
    'anyOf',
    'oneOf',
    'prefixItems',
})


# Keyword value is a map from arbitrary user-defined name/pattern to schema.
SCHEMA_MAP_KEYWORDS = frozenset({
    '$defs',
    'definitions',
    'properties',
    'patternProperties',
    'dependentSchemas',
})


def json_type_name(value: ta.Any) -> str:
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'boolean'
    if isinstance(value, int) and not isinstance(value, bool):
        return 'integer'
    if isinstance(value, float):
        return 'number'
    if isinstance(value, str):
        return 'string'
    if isinstance(value, list):
        return 'array'
    if isinstance(value, dict):
        return 'object'
    return type(value).__name__


def looks_like_schema(value: ta.Any) -> bool:
    """Best-effort check for draft-04 'dependencies' values, etc."""

    return isinstance(value, (dict, bool))


def count_keyword_value_features(counts: collections.Counter[str], key: str, value: ta.Any) -> None:
    """Count useful derived/value-level features in addition to raw keywords."""

    if key == 'type':
        if isinstance(value, str):
            counts[f'type.{value}'] += 1
        elif isinstance(value, list):
            counts['type.union_array'] += 1
            for item in value:
                if isinstance(item, str):
                    counts[f'type.{item}'] += 1
                else:
                    counts[f'type.<non_string:{json_type_name(item)}>'] += 1
        else:
            counts[f'type.<nonstandard:{json_type_name(value)}>'] += 1

    elif key == 'enum':
        if isinstance(value, list):
            counts['enum.count'] += 1
            counts['enum.values.total'] += len(value)
            for item in value:
                counts[f'enum.value_type.{json_type_name(item)}'] += 1
        else:
            counts[f'enum.<non_array:{json_type_name(value)}>'] += 1

    elif key == 'const':
        counts[f'const.value_type.{json_type_name(value)}'] += 1

    elif key in ('allOf', 'anyOf', 'oneOf'):
        if isinstance(value, list):
            counts[f'{key}.count'] += 1
            counts[f'{key}.alternatives.total'] += len(value)
        else:
            counts[f'{key}.<non_array:{json_type_name(value)}>'] += 1

    elif key in ('properties', 'patternProperties', '$defs', 'definitions', 'dependentSchemas'):
        if isinstance(value, dict):
            counts[f'{key}.entries.total'] += len(value)
        else:
            counts[f'{key}.<non_object:{json_type_name(value)}>'] += 1

    elif key == 'required':
        if isinstance(value, list):
            counts['required.arrays'] += 1
            counts['required.names.total'] += len(value)
        else:
            counts[f'required.<non_array:{json_type_name(value)}>'] += 1

    elif key == 'dependentRequired':
        if isinstance(value, dict):
            counts['dependentRequired.entries.total'] += len(value)
            for dep_value in value.values():
                if isinstance(dep_value, list):
                    counts['dependentRequired.names.total'] += len(dep_value)
        else:
            counts[f'dependentRequired.<non_object:{json_type_name(value)}>'] += 1

    elif key == 'dependencies':
        # Draft-04-ish: values may be either schema dependencies or property-name arrays.
        if isinstance(value, dict):
            counts['dependencies.entries.total'] += len(value)
            for dep_value in value.values():
                if isinstance(dep_value, list):
                    counts['dependencies.property_arrays'] += 1
                    counts['dependencies.property_names.total'] += len(dep_value)
                elif looks_like_schema(dep_value):
                    counts['dependencies.schema_values'] += 1
                else:
                    counts[f'dependencies.value.<{json_type_name(dep_value)}>'] += 1
        else:
            counts[f'dependencies.<non_object:{json_type_name(value)}>'] += 1

    elif key == 'items':
        if isinstance(value, list):
            # Older tuple-validation style.
            counts['items.tuple_array'] += 1
            counts['items.tuple_entries.total'] += len(value)
        elif isinstance(value, bool):
            counts[f'items.boolean.{str(value).lower()}'] += 1
        elif isinstance(value, dict):
            counts['items.schema'] += 1
        else:
            counts[f'items.<non_schema:{json_type_name(value)}>'] += 1

    elif key in ('additionalProperties', 'unevaluatedProperties', 'unevaluatedItems', 'additionalItems'):
        if isinstance(value, bool):
            counts[f'{key}.boolean.{str(value).lower()}'] += 1
        elif isinstance(value, dict):
            counts[f'{key}.schema'] += 1
        else:
            counts[f'{key}.<non_schema:{json_type_name(value)}>'] += 1

    elif key == '$ref':
        if isinstance(value, str):
            if value.startswith('#'):
                counts['$ref.internal'] += 1
            else:
                counts['$ref.external_or_uri'] += 1
        else:
            counts[f'$ref.<non_string:{json_type_name(value)}>'] += 1

    elif key == 'format':
        if isinstance(value, str):
            counts[f'format.{value}'] += 1
        else:
            counts[f'format.<non_string:{json_type_name(value)}>'] += 1

    elif key == 'nullable':
        if isinstance(value, bool):
            counts[f'nullable.{str(value).lower()}'] += 1
        else:
            counts[f'nullable.<non_boolean:{json_type_name(value)}>'] += 1


def visit_schema(schema: ta.Any, counts: collections.Counter[str]) -> None:
    """
    Visit a JSON Schema value.

    JSON Schema allows boolean schemas. Object schemas are dicts.
    """

    if isinstance(schema, bool):
        counts['schema.boolean'] += 1
        counts[f'schema.boolean.{str(schema).lower()}'] += 1
        return

    if not isinstance(schema, dict):
        # Not valid as a schema in modern drafts, but useful for diagnostics.
        counts[f'schema.<non_object:{json_type_name(schema)}>'] += 1
        return

    counts['schema.object'] += 1

    for key, value in schema.items():
        if key in KNOWN_KEYWORDS:
            counts[f'keyword.{key}'] += 1
            count_keyword_value_features(counts, key, value)
        elif key.startswith('x-'):
            counts['keyword.<extension:x-*>'] += 1
            counts[f'keyword.<extension:{key}>'] += 1
        else:
            # In a schema object, unknown keys are custom/unknown keywords. This will not count property names inside
            # "properties", because "properties" is handled as a schema map below.
            counts['keyword.<unknown>'] += 1
            counts[f'keyword.<unknown:{key}>'] += 1

        # Traverse into places that are known to contain schemas.
        if key in SCHEMA_VALUE_KEYWORDS:
            visit_schema(value, counts)

        elif key in SCHEMA_ARRAY_KEYWORDS:
            if isinstance(value, list):
                for item in value:
                    visit_schema(item, counts)

        elif key in SCHEMA_MAP_KEYWORDS:
            if isinstance(value, dict):
                for item in value.values():
                    visit_schema(item, counts)

        elif key == 'items':
            if isinstance(value, list):
                for item in value:
                    visit_schema(item, counts)
            elif looks_like_schema(value):
                visit_schema(value, counts)

        elif key == 'dependencies':
            # Draft-04-ish: value can be:
            #   "foo": ["bar", "baz"]
            # or:
            #   "foo": { ... schema ... }
            if isinstance(value, dict):
                for item in value.values():
                    if looks_like_schema(item):
                        visit_schema(item, counts)

        elif key == 'dependentRequired':
            # Not schema-bearing.
            pass


def load_json_file(path: str) -> ta.Any:
    if path == '-':
        return json.load(sys.stdin)
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def merge_counts(paths: ta.Iterable[str]) -> collections.Counter[str]:
    counts: collections.Counter[str] = collections.Counter()
    for path in paths:
        document = load_json_file(path)
        visit_schema(document, counts)
    return counts


def print_text_counts(counts: collections.Counter[str], *, sort_by_count: bool) -> None:
    if sort_by_count:
        items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    else:
        items = sorted(counts.items(), key=lambda kv: kv[0])

    width = max((len(k) for k, _ in items), default=0)
    for key, count in items:
        print(f'{key:<{width}}  {count}')


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'paths',
        nargs='*',
        help="JSON Schema files. Use '-' or omit paths to read stdin.",
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Emit counts as JSON.',
    )
    parser.add_argument(
        '--sort-by-count',
        action='store_true',
        help='Sort descending by count instead of alphabetically.',
    )
    args = parser.parse_args(argv)

    paths = args.paths or ['-']
    counts = merge_counts(paths)

    if args.json:
        print(json.dumps(dict(sorted(counts.items())), indent=2, sort_keys=True))
    else:
        print_text_counts(counts, sort_by_count=args.sort_by_count)

    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
