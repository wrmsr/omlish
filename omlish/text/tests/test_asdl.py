from ... import lang
from .. import asdl


def test_asdl():
    asdl_src = lang.get_relative_resources(globals=globals())['mini-python.asdl'].read_bytes().decode('utf-8')
    flat_nodes = asdl.flatten(asdl.AsdlParser().parse(asdl_src))
    node_fields = asdl.build_fields_info(flat_nodes)
    assert node_fields == {
        'expr': {
            'col_offset': ('int', 1),
            'end_col_offset': ('int', '?'),
            'end_lineno': ('int', '?'),
            'lineno': ('int', 1),
        },
        'BoolOp': {
            'op': ('boolop', 1),
            'values': ('expr', '*'),
        },
        'BinOp': {
            'left': ('expr', 1),
            'op': ('operator', 1),
            'right': ('expr', 1),
        },
        'UnaryOp': {
            'op': ('unaryop', 1),
            'operand': ('expr', 1),
        },
        'Constant': {
            'kind': ('string', '?'),
            'value': ('constant', 1),
        },
    }
