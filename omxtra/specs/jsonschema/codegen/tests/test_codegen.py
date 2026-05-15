import importlib.util
import os.path
import sys
import typing as ta

import pytest

from omlish import check
from omlish import marshal as msh
from omlish.specs import jsonschema as js

from ..errors import UnresolvedRefError
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


def _assert_unsupported(
        obj: ta.Mapping[str, ta.Any],
        path: tuple[str | int, ...],
        *,
        allow_unknown: bool = False,
) -> None:
    kws = _parse(obj, allow_unknown=allow_unknown)

    with pytest.raises(UnsupportedSchemaError) as ex:
        JsonSchemaCodeGen(kws).gen_module()

    assert ex.value.path == path


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


def test_object_const_field_codegen_marshal_round_trip(tmp_path):
    mod = _generate_import(tmp_path, {
        '$defs': {
            'AudioContent': {
                'type': 'object',
                'required': ['type', 'data'],
                'properties': {
                    'type': {'type': 'string', 'const': 'audio'},
                    'data': {'type': 'string'},
                },
            },
        },
    })

    obj = mod.AudioContent(data='abc')
    assert msh.marshal(obj, mod.AudioContent) == {
        'type': 'audio',
        'data': 'abc',
    }

    assert msh.unmarshal({
        'type': 'audio',
        'data': 'abc',
    }, mod.AudioContent) == obj


def test_scalar_const_and_field_enum_codegen_marshal_round_trip(tmp_path):
    mod = _generate_import(tmp_path, {
        '$defs': {
            'LiteralHolder': {
                'type': 'object',
                'required': ['enabled', 'version', 'mode'],
                'properties': {
                    'enabled': {'type': 'boolean', 'const': True},
                    'version': {'type': 'integer', 'const': 2},
                    'mode': {'type': 'string', 'enum': ['fast', 'slow']},
                },
            },
        },
    })

    obj = mod.LiteralHolder(mode='fast')
    assert msh.marshal(obj, mod.LiteralHolder) == {
        'enabled': True,
        'version': 2,
        'mode': 'fast',
    }

    assert msh.unmarshal({
        'enabled': True,
        'version': 2,
        'mode': 'slow',
    }, mod.LiteralHolder) == mod.LiteralHolder(mode='slow')


def test_nullable_and_primitive_union_codegen_marshal_round_trip(tmp_path):
    mod = _generate_import(tmp_path, {
        '$defs': {
            'ScalarHolder': {
                'type': 'object',
                'required': ['id', 'value'],
                'properties': {
                    'id': {'type': 'string'},
                    'count': {'type': ['integer', 'null']},
                    'value': {
                        'anyOf': [
                            {'type': 'string'},
                            {'type': 'integer'},
                            {'type': 'null'},
                        ],
                    },
                },
            },
        },
    })

    obj = mod.ScalarHolder(id='one', value=42)
    assert msh.marshal(obj, mod.ScalarHolder) == {
        'id': 'one',
        'value': 42,
    }

    assert msh.unmarshal({
        'id': 'two',
        'count': None,
        'value': 'x',
    }, mod.ScalarHolder) == mod.ScalarHolder(id='two', count=None, value='x')


def test_arrays_maps_and_refs_codegen_marshal_round_trip(tmp_path):
    mod = _generate_import(tmp_path, {
        '$defs': {
            'Role': {
                'enum': ['admin', 'user'],
                'type': 'string',
            },
            'User': {
                'type': 'object',
                'required': ['name', 'role'],
                'properties': {
                    'name': {'type': 'string'},
                    'role': {'$ref': '#/$defs/Role'},
                },
            },
            'Directory': {
                'type': 'object',
                'required': ['users', 'scores'],
                'properties': {
                    'users': {
                        'type': 'array',
                        'items': {'$ref': '#/$defs/User'},
                    },
                    'labels': {
                        'type': 'array',
                        'items': {'type': 'string'},
                    },
                    'scores': {
                        'type': 'object',
                        'additionalProperties': {'type': 'integer'},
                    },
                },
            },
        },
    })

    obj = mod.Directory(
        users=[mod.User(name='alice', role='admin')],
        scores={'alice': 10},
    )
    assert msh.marshal(obj, mod.Directory) == {
        'users': [
            {
                'name': 'alice',
                'role': 'admin',
            },
        ],
        'scores': {
            'alice': 10,
        },
    }

    assert msh.unmarshal({
        'users': [
            {
                'name': 'bob',
                'role': 'user',
            },
        ],
        'labels': ['remote'],
        'scores': {
            'bob': 7,
        },
    }, mod.Directory) == mod.Directory(
        users=(mod.User(name='bob', role='user'),),
        labels=('remote',),
        scores={'bob': 7},
    )


def test_object_additional_properties_false_codegen_marshal_round_trip(tmp_path):
    mod = _generate_import(tmp_path, {
        '$defs': {
            'ClosedObject': {
                'type': 'object',
                'additionalProperties': False,
                'required': ['name'],
                'properties': {
                    'name': {'type': 'string'},
                },
            },
        },
    })

    obj = mod.ClosedObject(name='alice')
    assert msh.marshal(obj, mod.ClosedObject) == {
        'name': 'alice',
    }

    assert msh.unmarshal({
        'name': 'bob',
    }, mod.ClosedObject) == mod.ClosedObject(name='bob')


def test_array_inline_object_codegen_marshal_round_trip(tmp_path):
    mod = _generate_import(tmp_path, {
        '$defs': {
            'Thread': {
                'type': 'object',
                'required': ['messages'],
                'properties': {
                    'messages': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'required': ['text', 'author'],
                            'properties': {
                                'text': {'type': 'string'},
                                'author': {
                                    'type': 'object',
                                    'required': ['name'],
                                    'properties': {
                                        'name': {'type': 'string'},
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
    })

    obj = mod.Thread(messages=[
        mod.Thread.MessagesItem(
            text='hello',
            author=mod.Thread.MessagesItem.Author(name='alice'),
        ),
    ])
    assert msh.marshal(obj, mod.Thread) == {
        'messages': [
            {
                'text': 'hello',
                'author': {
                    'name': 'alice',
                },
            },
        ],
    }

    assert msh.unmarshal({
        'messages': [
            {
                'text': 'hi',
                'author': {
                    'name': 'bob',
                },
            },
        ],
    }, mod.Thread) == mod.Thread(messages=(
        mod.Thread.MessagesItem(
            text='hi',
            author=mod.Thread.MessagesItem.Author(name='bob'),
        ),
    ))


def test_explicit_open_any_shapes_codegen_marshal_round_trip(tmp_path):
    mod = _generate_import(tmp_path, {
        '$defs': {
            'OpenHolder': {
                'type': 'object',
                'required': ['payload', 'items', 'attrs'],
                'properties': {
                    'payload': {},
                    'items': {'type': 'array'},
                    'attrs': {
                        'type': 'object',
                        'additionalProperties': True,
                    },
                    'extra': {
                        'type': 'object',
                        'additionalProperties': {},
                    },
                },
            },
        },
    })

    obj = mod.OpenHolder(
        payload={'kind': 'raw'},
        items=[1, 'two'],
        attrs={'enabled': True},
    )
    assert msh.marshal(obj, mod.OpenHolder) == {
        'payload': {'kind': 'raw'},
        'items': [1, 'two'],
        'attrs': {'enabled': True},
    }

    assert msh.unmarshal({
        'payload': ['raw'],
        'items': [{'x': 1}],
        'attrs': {'enabled': True},
        'extra': {'nested': {'x': 1}},
    }, mod.OpenHolder) == mod.OpenHolder(
        payload=['raw'],
        items=({'x': 1},),
        attrs={'enabled': True},
        extra={'nested': {'x': 1}},
    )


def test_all_of_object_flattening_codegen_marshal_round_trip(tmp_path):
    mod = _generate_import(tmp_path, {
        '$defs': {
            'BaseItem': {
                'type': 'object',
                'required': ['id'],
                'properties': {
                    'id': {'type': 'string'},
                },
            },
            'NamedItem': {
                'allOf': [
                    {'$ref': '#/$defs/BaseItem'},
                    {
                        'type': 'object',
                        'required': ['name'],
                        'properties': {
                            'name': {'type': 'string'},
                        },
                    },
                ],
            },
        },
    })

    obj = mod.NamedItem(id='i1', name='Item')
    assert msh.marshal(obj, mod.NamedItem) == {
        'id': 'i1',
        'name': 'Item',
    }

    assert msh.unmarshal({
        'id': 'i2',
        'name': 'Other',
    }, mod.NamedItem) == mod.NamedItem(id='i2', name='Other')


def test_all_of_multiple_refs_and_nested_defs_codegen_marshal_round_trip(tmp_path):
    mod = _generate_import(tmp_path, {
        '$defs': {
            'BaseItem': {
                'type': 'object',
                'required': ['id'],
                'properties': {
                    'id': {'type': 'string'},
                },
            },
            'NamedItem': {
                'allOf': [
                    {'$ref': '#/$defs/BaseItem'},
                    {
                        'type': 'object',
                        'required': ['name', 'details'],
                        'properties': {
                            'name': {'type': 'string'},
                            'details': {
                                'type': 'object',
                                'required': ['enabled'],
                                'properties': {
                                    'enabled': {'type': 'boolean'},
                                },
                            },
                        },
                    },
                ],
            },
            'VersionedItem': {
                'type': 'object',
                'required': ['version'],
                'properties': {
                    'version': {'type': 'integer'},
                },
            },
            'CompleteItem': {
                'allOf': [
                    {'$ref': '#/$defs/NamedItem'},
                    {'$ref': '#/$defs/VersionedItem'},
                    {
                        'type': 'object',
                        'properties': {
                            'tags': {
                                'type': 'array',
                                'items': {'type': 'string'},
                            },
                        },
                    },
                ],
            },
        },
    })

    obj = mod.CompleteItem(
        id='i1',
        name='Item',
        details=mod.NamedItem.Details(enabled=True),
        version=2,
        tags=['a'],
    )
    assert msh.marshal(obj, mod.CompleteItem) == {
        'id': 'i1',
        'name': 'Item',
        'details': {
            'enabled': True,
        },
        'version': 2,
        'tags': ['a'],
    }

    assert msh.unmarshal({
        'id': 'i2',
        'name': 'Other',
        'details': {
            'enabled': False,
        },
        'version': 3,
    }, mod.CompleteItem) == mod.CompleteItem(
        id='i2',
        name='Other',
        details=mod.NamedItem.Details(enabled=False),
        version=3,
    )


def test_top_level_const_one_of_enum_codegen_marshal_round_trip(tmp_path):
    mod = _generate_import(tmp_path, {
        '$defs': {
            'Status': {
                'oneOf': [
                    {'type': 'string', 'const': 'pending'},
                    {'type': 'string', 'const': 'done'},
                ],
            },
            'Task': {
                'type': 'object',
                'required': ['status'],
                'properties': {
                    'status': {'$ref': '#/$defs/Status'},
                },
            },
        },
    })

    obj = mod.Task(status='pending')
    assert msh.marshal(obj, mod.Task) == {
        'status': 'pending',
    }

    assert msh.unmarshal({
        'status': 'done',
    }, mod.Task) == mod.Task(status='done')


def test_snake_field_naming_codegen_marshal_round_trip(tmp_path):
    mod = _generate_import(tmp_path, {
        '$defs': {
            'SnakeRecord': {
                'type': 'object',
                'required': ['display_name'],
                'properties': {
                    'display_name': {'type': 'string'},
                    'updated_at': {'type': 'string'},
                },
            },
        },
    })

    obj = mod.SnakeRecord(display_name='Alice')
    assert msh.marshal(obj, mod.SnakeRecord) == {
        'display_name': 'Alice',
    }

    assert msh.unmarshal({
        'display_name': 'Bob',
        'updated_at': 'now',
    }, mod.SnakeRecord) == mod.SnakeRecord(display_name='Bob', updated_at='now')


def test_inline_object_codegen_marshal_round_trip(tmp_path):
    mod = _generate_import(tmp_path, {
        '$defs': {
            'CallToolRequest': {
                'type': 'object',
                'required': ['method', 'params'],
                'properties': {
                    'method': {'type': 'string', 'const': 'tools/call'},
                    'params': {
                        'type': 'object',
                        'required': ['name'],
                        'properties': {
                            'name': {'type': 'string'},
                            'arguments': {
                                'type': 'object',
                                'additionalProperties': {},
                            },
                            'nestedValue': {
                                'type': 'object',
                                'required': ['leaf'],
                                'properties': {
                                    'leaf': {'type': 'integer'},
                                },
                            },
                            'records': {
                                'type': 'object',
                                'additionalProperties': {
                                    'type': 'object',
                                    'required': ['id'],
                                    'properties': {
                                        'id': {'type': 'string'},
                                    },
                                },
                            },
                            'includeContext': {
                                'type': 'string',
                                'enum': ['allServers', 'none', 'thisServer'],
                            },
                        },
                    },
                },
            },
        },
    })

    obj = mod.CallToolRequest(
        params=mod.CallToolRequest.Params(
            name='search',
            arguments={'query': 'x'},
            nested_value=mod.CallToolRequest.Params.NestedValue(leaf=420),
            records={
                'a': mod.CallToolRequest.Params.RecordsValue(id='one'),
            },
            include_context='thisServer',
        ),
    )

    assert msh.marshal(obj, mod.CallToolRequest) == {
        'method': 'tools/call',
        'params': {
            'name': 'search',
            'arguments': {'query': 'x'},
            'nestedValue': {
                'leaf': 420,
            },
            'records': {
                'a': {
                    'id': 'one',
                },
            },
            'includeContext': 'thisServer',
        },
    }

    assert msh.unmarshal({
        'method': 'tools/call',
        'params': {
            'name': 'search',
            'arguments': {'query': 'x'},
            'nestedValue': {
                'leaf': 420,
            },
            'records': {
                'a': {
                    'id': 'one',
                },
            },
            'includeContext': 'thisServer',
        },
    }, mod.CallToolRequest) == obj


def test_ref_alias_codegen_marshal_round_trip(tmp_path):
    mod = _generate_import(tmp_path, {
        '$defs': {
            'Result': {
                'type': 'object',
                'properties': {
                    '_meta': {'type': 'object', 'additionalProperties': True},
                },
            },
            'EmptyResult': {
                '$ref': '#/$defs/Result',
            },
        },
    })

    obj = mod.Result(meta={'trace': 1})
    assert msh.marshal(obj, mod.EmptyResult) == {
        '_meta': {'trace': 1},
    }

    assert msh.unmarshal({
        '_meta': {'trace': 1},
    }, mod.EmptyResult) == obj


def test_definitions_ref_codegen_marshal_round_trip(tmp_path):
    mod = _generate_import(tmp_path, {
        'definitions': {
            'Target': {
                'type': 'object',
                'required': ['name'],
                'properties': {
                    'name': {'type': 'string'},
                },
            },
            'Holder': {
                'type': 'object',
                'required': ['target'],
                'properties': {
                    'target': {'$ref': '#/definitions/Target'},
                },
            },
        },
    })

    obj = mod.Holder(target=mod.Target(name='alice'))
    assert msh.marshal(obj, mod.Holder) == {
        'target': {
            'name': 'alice',
        },
    }

    assert msh.unmarshal({
        'target': {
            'name': 'bob',
        },
    }, mod.Holder) == mod.Holder(target=mod.Target(name='bob'))


def test_json_pointer_escaped_ref_codegen_marshal_round_trip(tmp_path):
    mod = _generate_import(tmp_path, {
        '$defs': {
            'Foo/Bar': {
                'type': 'object',
                'required': ['name'],
                'properties': {
                    'name': {'type': 'string'},
                },
            },
            'Holder': {
                'type': 'object',
                'required': ['target'],
                'properties': {
                    'target': {'$ref': '#/$defs/Foo~1Bar'},
                },
            },
        },
    })

    obj = mod.Holder(target=mod.FooBar(name='alice'))
    assert msh.marshal(obj, mod.Holder) == {
        'target': {
            'name': 'alice',
        },
    }


def test_unsupported_keyword_explodes():
    _assert_unsupported({
        '$defs': {
            'Thing': {
                'type': 'object',
                'patternProperties': {
                    '^x-': {'type': 'string'},
                },
            },
        },
    }, ('$defs', 'Thing'), allow_unknown=True)


def test_unsupported_non_x_unknown_keyword_explodes():
    _assert_unsupported({
        '$defs': {
            'Thing': {
                'type': 'object',
                'unknownKeyword': True,
                'properties': {
                    'name': {'type': 'string'},
                },
            },
        },
    }, ('$defs', 'Thing'), allow_unknown=True)


def test_unsupported_plain_one_of_union_explodes():
    _assert_unsupported({
        '$defs': {
            'Thing': {
                'oneOf': [
                    {'$ref': '#/$defs/Foo'},
                    {'$ref': '#/$defs/Bar'},
                ],
            },
            'Foo': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                },
            },
            'Bar': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string'},
                },
            },
        },
    }, ('$defs', 'Thing'))


def test_unsupported_complex_field_any_of_explodes():
    _assert_unsupported({
        '$defs': {
            'Foo': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                },
            },
            'Bar': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string'},
                },
            },
            'Thing': {
                'type': 'object',
                'properties': {
                    'value': {
                        'anyOf': [
                            {'$ref': '#/$defs/Foo'},
                            {'$ref': '#/$defs/Bar'},
                        ],
                    },
                },
            },
        },
    }, ('$defs', 'Thing', 'properties', 'value'))


def test_unsupported_complex_top_level_any_of_explodes():
    _assert_unsupported({
        '$defs': {
            'Foo': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                },
            },
            'Bar': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string'},
                },
            },
            'Thing': {
                'anyOf': [
                    {'$ref': '#/$defs/Foo'},
                    {'$ref': '#/$defs/Bar'},
                ],
            },
        },
    }, ('$defs', 'Thing'))


def test_unsupported_non_empty_unconstrained_schema_explodes():
    _assert_unsupported({
        '$defs': {
            'Thing': {
                'type': 'object',
                'properties': {
                    'payload': {
                        'default': {},
                    },
                },
            },
        },
    }, ('$defs', 'Thing', 'properties', 'payload'))


def test_unsupported_top_level_empty_enum_explodes():
    _assert_unsupported({
        '$defs': {
            'Thing': {
                'type': 'string',
                'enum': [],
            },
        },
    }, ('$defs', 'Thing'))


def test_unsupported_top_level_non_string_enum_explodes():
    _assert_unsupported({
        '$defs': {
            'Thing': {
                'type': 'integer',
                'enum': [1, 2],
            },
        },
    }, ('$defs', 'Thing'))


def test_unsupported_field_empty_enum_explodes():
    _assert_unsupported({
        '$defs': {
            'Thing': {
                'type': 'object',
                'properties': {
                    'mode': {
                        'type': 'string',
                        'enum': [],
                    },
                },
            },
        },
    }, ('$defs', 'Thing', 'properties', 'mode'))


def test_unsupported_field_mixed_enum_explodes():
    _assert_unsupported({
        '$defs': {
            'Thing': {
                'type': 'object',
                'properties': {
                    'mode': {
                        'enum': ['fast', 1],
                    },
                },
            },
        },
    }, ('$defs', 'Thing', 'properties', 'mode'))


def test_unsupported_non_scalar_const_explodes():
    _assert_unsupported({
        '$defs': {
            'Thing': {
                'type': 'object',
                'properties': {
                    'kind': {
                        'const': {'type': 'x'},
                    },
                },
            },
        },
    }, ('$defs', 'Thing', 'properties', 'kind'))


def test_unsupported_non_string_discriminator_const_explodes():
    _assert_unsupported({
        '$defs': {
            'Cat': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                },
            },
            'Pet': {
                'discriminator': {'propertyName': 'type'},
                'oneOf': [
                    {
                        'type': 'object',
                        'properties': {
                            'type': {'type': 'integer', 'const': 1},
                        },
                        'allOf': [{'$ref': '#/$defs/Cat'}],
                    },
                ],
            },
        },
    }, ('$defs', 'Pet', 'oneOf', 0, 'properties', 'type'))


def test_unsupported_invalid_discriminator_shape_explodes():
    _assert_unsupported({
        '$defs': {
            'Pet': {
                'discriminator': 'type',
                'oneOf': [],
            },
        },
    }, ('$defs', 'Pet'))


def test_unsupported_object_with_open_additional_properties_explodes():
    _assert_unsupported({
        '$defs': {
            'Thing': {
                'type': 'object',
                'additionalProperties': True,
                'properties': {
                    'name': {'type': 'string'},
                },
            },
        },
    }, ('$defs', 'Thing'))


def test_unsupported_object_with_typed_additional_properties_explodes():
    _assert_unsupported({
        '$defs': {
            'Thing': {
                'type': 'object',
                'additionalProperties': {'type': 'string'},
                'properties': {
                    'name': {'type': 'string'},
                },
            },
        },
    }, ('$defs', 'Thing'))


def test_unsupported_object_with_inline_additional_properties_explodes():
    _assert_unsupported({
        '$defs': {
            'Thing': {
                'type': 'object',
                'additionalProperties': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'string'},
                    },
                },
                'properties': {
                    'name': {'type': 'string'},
                },
            },
        },
    }, ('$defs', 'Thing'))


def test_unsupported_external_ref_explodes():
    _assert_unsupported({
        '$defs': {
            'Thing': {
                '$ref': 'https://example.com/schema.json#/$defs/Other',
            },
        },
    }, ('$defs', 'Thing'))


def test_unsupported_nested_ref_explodes():
    _assert_unsupported({
        '$defs': {
            'Thing': {
                'type': 'object',
                'properties': {
                    'name': {'$ref': '#/$defs/Other/properties/name'},
                },
            },
            'Other': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                },
            },
        },
    }, ('$defs', 'Thing', 'properties', 'name'))


def test_unsupported_empty_ref_explodes():
    _assert_unsupported({
        '$defs': {
            'Thing': {
                '$ref': '#/$defs/',
            },
        },
    }, ('$defs', 'Thing'))


def test_unsupported_all_of_duplicate_json_field_explodes():
    _assert_unsupported({
        '$defs': {
            'Base': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string'},
                },
            },
            'Thing': {
                'allOf': [
                    {'$ref': '#/$defs/Base'},
                    {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                        },
                    },
                ],
            },
        },
    }, ())


def test_unsupported_all_of_duplicate_python_field_explodes():
    _assert_unsupported({
        '$defs': {
            'Base': {
                'type': 'object',
                'properties': {
                    'fooBar': {'type': 'string'},
                },
            },
            'Thing': {
                'allOf': [
                    {'$ref': '#/$defs/Base'},
                    {
                        'type': 'object',
                        'properties': {
                            'foo_bar': {'type': 'string'},
                        },
                    },
                ],
            },
        },
    }, ())


def test_unsupported_all_of_duplicate_nested_class_explodes():
    _assert_unsupported({
        '$defs': {
            'Base': {
                'type': 'object',
                'properties': {
                    'details': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string'},
                        },
                    },
                },
            },
            'Thing': {
                'allOf': [
                    {'$ref': '#/$defs/Base'},
                    {
                        'type': 'object',
                        'properties': {
                            'details': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string'},
                                },
                            },
                        },
                    },
                ],
            },
        },
    }, ())


def test_unsupported_object_duplicate_python_field_explodes():
    _assert_unsupported({
        '$defs': {
            'Thing': {
                'type': 'object',
                'properties': {
                    'fooBar': {'type': 'string'},
                    'foo_bar': {'type': 'string'},
                },
            },
        },
    }, ('$defs', 'Thing'))


def test_unresolved_all_of_ref_explodes():
    kws = _parse({
        '$defs': {
            'Thing': {
                'allOf': [
                    {'$ref': '#/$defs/Missing'},
                ],
            },
        },
    })

    with pytest.raises(UnresolvedRefError):
        JsonSchemaCodeGen(kws).gen_module()
