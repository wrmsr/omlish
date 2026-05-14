import importlib.util
import os.path
import sys

from omlish import check
from omlish import marshal as msh
from ommlds.specs.mcp.spec import spec_json_schema

from ..generator import JsonSchemaCodeGen


##


def test_mcp_codegen_import_and_marshal(tmp_path):
    src = JsonSchemaCodeGen(spec_json_schema()).gen_module()
    path = os.path.join(tmp_path, 'mcp_protocol.py')
    with open(path, 'w') as f:
        f.write(src)

    name = '_test_mcp_protocol_codegen'
    spec = check.not_none(importlib.util.spec_from_file_location(name, path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    check.not_none(spec.loader).exec_module(mod)

    req = mod.CallToolRequest(
        params=mod.CallToolRequest.Params(
            name='search',
            arguments={'query': 'x'},
        ),
    )
    assert msh.marshal(req, mod.CallToolRequest) == {
        'method': 'tools/call',
        'params': {
            'name': 'search',
            'arguments': {
                'query': 'x',
            },
        },
    }

    req2 = msh.unmarshal({
        'method': 'tools/call',
        'params': {
            'name': 'search',
            'arguments': {
                'query': 'x',
            },
        },
    }, mod.CallToolRequest)
    assert req2 == req
