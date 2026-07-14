import os.path

import yaml

from ..... import marshal as msh
from ...openapi import Openapi
from ..jsonschema import build_jsonschema


def test_build_jsonschema():
    with open(os.path.join(os.path.dirname(__file__), '../../tests/example.yml')) as f:
        yml_src = f.read()
    doc = yaml.safe_load(yml_src)

    api = msh.unmarshal(doc, Openapi)
    js = build_jsonschema(api)

    assert set(js.schema['$defs']) == {
        'Artist',
        'ParameterPageLimitQueryLimitSchema',
        'ParameterPageOffsetQueryOffsetSchema',
        'Response400ErrorApplicationJsonSchema',
        'GetArtistsResponse200ApplicationJsonSchema',
        'GetArtistsUsernameParameterPathUsernameSchema',
        'GetArtistsUsernameResponse200ApplicationJsonSchema',
    }

    assert js.schema['$defs']['GetArtistsResponse200ApplicationJsonSchema']['items'] == {
        '$ref': '#/$defs/Artist',
    }

    assert js.schema['anyOf'] == [
        {'$ref': '#/$defs/Artist'},
        {'$ref': '#/$defs/ParameterPageLimitQueryLimitSchema'},
        {'$ref': '#/$defs/ParameterPageOffsetQueryOffsetSchema'},
        {'$ref': '#/$defs/Response400ErrorApplicationJsonSchema'},
        {'$ref': '#/$defs/GetArtistsResponse200ApplicationJsonSchema'},
        {'$ref': '#/$defs/GetArtistsUsernameParameterPathUsernameSchema'},
        {'$ref': '#/$defs/GetArtistsUsernameResponse200ApplicationJsonSchema'},
    ]
