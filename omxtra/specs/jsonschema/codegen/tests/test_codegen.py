import importlib.util
import os.path
import sys
import typing as ta

import pytest

from omlish import check
from omlish import marshal as msh
from omlish.specs import jsonschema as js

from ..errors import UnsupportedSchemaError
from ..generator import JsonSchemaCodeGen


##


def _parse(obj: ta.Mapping[str, ta.Any], *, allow_unknown: bool = False) -> js.Keywords:
    return js.KeywordParser(
        allow_unknown=allow_unknown,
        allow_specific_unknowns={'discriminator'},
    ).parse_keywords(obj)


def _generate_import(tmp_path, obj: ta.Mapping[str, ta.Any]):
    src = JsonSchemaCodeGen(_parse(obj)).gen_module()
    path = os.path.join(tmp_path, 'generated.py')
    with open(path, 'w') as f:
        f.write(src)

    name = f'_test_jsonschema_codegen_{id(obj)}'
    spec = check.not_none(importlib.util.spec_from_file_location(name, path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    check.not_none(spec.loader).exec_module(mod)
    return mod


def test_object_codegen_marshal_round_trip(tmp_path):
    mod = _generate_import(tmp_path, {
        '$defs': {
            'UserProfile': {
                'type': 'object',
                'required': ['userName'],
                'properties': {
                    'userName': {'type': 'string'},
                    'age': {'type': 'integer'},
                    'tags': {'type': 'array', 'items': {'type': 'string'}},
                    '_meta': {'type': 'object', 'additionalProperties': True},
                },
            },
        },
    })

    obj = mod.UserProfile(
        user_name='alice',
        tags=['admin'],
        meta={'trace': 1},
    )

    mv = msh.marshal(obj, mod.UserProfile)
    assert mv == {
        'userName': 'alice',
        'tags': ['admin'],
        '_meta': {'trace': 1},
    }

    obj2 = msh.unmarshal({
        'userName': 'bob',
        'age': 42,
        'tags': ['user'],
    }, mod.UserProfile)
    assert obj2 == mod.UserProfile(user_name='bob', age=42, tags=('user',))


def test_discriminated_union_codegen_marshal_round_trip(tmp_path):
    mod = _generate_import(tmp_path, {
        '$defs': {
            'Cat': {
                'type': 'object',
                'required': ['name'],
                'properties': {
                    'name': {'type': 'string'},
                },
            },
            'Dog': {
                'type': 'object',
                'required': ['name'],
                'properties': {
                    'name': {'type': 'string'},
                },
            },
            'Pet': {
                'discriminator': {'propertyName': 'type'},
                'oneOf': [
                    {
                        'type': 'object',
                        'required': ['type'],
                        'properties': {
                            'type': {'type': 'string', 'const': 'cat'},
                        },
                        'allOf': [{'$ref': '#/$defs/Cat'}],
                    },
                    {
                        'type': 'object',
                        'required': ['type'],
                        'properties': {
                            'type': {'type': 'string', 'const': 'dog'},
                        },
                        'allOf': [{'$ref': '#/$defs/Dog'}],
                    },
                ],
            },
        },
    })

    obj = mod.CatPet(name='miette')
    assert msh.marshal(obj, mod.Pet) == {
        'name': 'miette',
        'type': 'cat',
    }

    obj2 = msh.unmarshal({
        'type': 'dog',
        'name': 'fido',
    }, mod.Pet)
    assert obj2 == mod.DogPet(name='fido')


def test_unsupported_keyword_explodes():
    kws = _parse({
        '$defs': {
            'Thing': {
                'type': 'object',
                'patternProperties': {
                    '^x-': {'type': 'string'},
                },
            },
        },
    }, allow_unknown=True)

    with pytest.raises(UnsupportedSchemaError):
        JsonSchemaCodeGen(kws).gen_module()
