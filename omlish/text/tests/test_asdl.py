from .. import asdl
from ... import lang


def test_asdl():
    asdl_src = lang.get_relative_resources(globals=globals())['mini-python.asdl'].read_bytes().decode('utf-8')
    flat_nodes = asdl.flatten(asdl.AsdlParser().parse(asdl_src))
    node_fields = asdl.build_fields_info(flat_nodes)
    assert node_fields == {
        'BinOp': {
            'col_offset': ('int', 1),
            'end_col_offset': ('int', '?'),
            'end_lineno': ('int', '?'),
            'left': ('expr', 1),
            'lineno': ('int', 1),
            'op': ('operator', 1),
            'right': ('expr', 1),
        },
        'BoolOp': {
            'col_offset': ('int', 1),
            'end_col_offset': ('int', '?'),
            'end_lineno': ('int', '?'),
            'lineno': ('int', 1),
            'op': ('boolop', 1),
            'values': ('expr', '*'),
        },
        'Constant': {
            'col_offset': ('int', 1),
            'end_col_offset': ('int', '?'),
            'end_lineno': ('int', '?'),
            'kind': ('string', '?'),
            'lineno': ('int', 1),
            'value': ('constant', 1),
        },
        'UnaryOp': {
            'col_offset': ('int', 1),
            'end_col_offset': ('int', '?'),
            'end_lineno': ('int', '?'),
            'lineno': ('int', 1),
            'op': ('unaryop', 1),
            'operand': ('expr', 1),
        },
        'expr': {
            'col_offset': ('int', 1),
            'end_col_offset': ('int', '?'),
            'end_lineno': ('int', '?'),
            'lineno': ('int', 1)},
    }
