import importlib.util
import os.path
import sys

from omlish import check
from omlish import marshal as msh

from ..generator import JsonSchemaCodeGen


##


def test_acp_codegen_import_and_marshal(tmp_path):
    from omllm.specs.acp.spec import spec_json_schema

    src = JsonSchemaCodeGen(spec_json_schema()).gen_module()
    path = os.path.join(tmp_path, 'acp_protocol.py')
    with open(path, 'w') as f:
        f.write(src)

    name = '_test_acp_protocol_codegen'
    spec = check.not_none(importlib.util.spec_from_file_location(name, path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    check.not_none(spec.loader).exec_module(mod)

    ac = mod.AgentCapabilities(load_session=True, meta={'trace': 1})
    assert msh.marshal(ac, mod.AgentCapabilities) == {
        'loadSession': True,
        '_meta': {'trace': 1},
    }

    tc = mod.TextContentBlock(text='hello')
    assert msh.marshal(tc, mod.ContentBlock) == {
        'text': 'hello',
        'type': 'text',
    }

    tc2 = msh.unmarshal({
        'type': 'text',
        'text': 'hello',
    }, mod.ContentBlock)
    assert tc2 == tc
