"""
TODO:
 - marshal 'external object... infos?'
 - gen map from ast node name -> map from field name to field type
"""
import ast
import os.path

from omlish import collections as col
from omlish import lang
from omlish import marshal as msh

from omlish.text import asdl


def _main() -> None:
    asdl_src = lang.get_relative_resources(globals=globals())['python-3.12.asdl'].read_bytes().decode('utf-8')
    py_nodes = asdl.flatten(asdl.AsdlParser().parse(asdl_src))
    py_node_fields = asdl.build_fields_info(py_nodes)
    print(py_node_fields)

    ##

    src_file = os.path.join(os.path.dirname(__file__), 'resolve.py')
    with open(src_file) as f:
        src = f.read()

    root = ast.parse(src, src_file)
    print(root)

    ##

    deprecated = {
        'AugLoad',
        'AugStore',
        'ExtSlice',
        'Index',
        'Param',
        'Suite',
        'slice',
    }
    ast_cls_lst = [
        v
        for a in dir(ast)
        if isinstance(v := getattr(ast, a), type)
        and v is not ast.AST
        and issubclass(v, ast.AST)
        and v.__name__ not in deprecated
    ]
    ast_cls_dct = col.make_map_by(lambda c: c.__name__, ast_cls_lst, strict=True)
    missing = [ast_cls_dct[n] for n in set(ast_cls_dct) - set(py_nodes)]
    consts, missing_non_consts = col.partition(missing, lambda m: issubclass(m, ast.Constant))
    if missing_non_consts:
        raise Exception('Missing non-const subclasses', missing_non_consts)

    ast_poly = msh.Polymorphism(ast.AST, [msh.Impl(ty, tag) for tag, ty in ast_cls_dct.items()])
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(ast_poly)]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(ast_poly)]

    # _attributes = ()
    # _fields = ()


if __name__ == '__main__':
    _main()
