"""
TODO:
 - marshal 'external object... infos?'
 - gen map from ast node name -> map from field name to field type

==

deprecated in 3.12:
class AugLoad(expr_context):
class AugStore(expr_context):
class ExtSlice(slice):
class Index(slice):
class Param(expr_context):
class Suite(mod):
class slice(AST):

still missing:
Bytes
Ellipsis
EnhancedAST
NameConstant
Num
Str
"""
import ast
import os.path

from omlish import collections as col
from omlish import lang
from omlish import marshal as msh

from . import asdl


def _main() -> None:
    asdl_src = lang.get_relative_resources(globals=globals())['python-3.12.asdl'].read_bytes().decode('utf-8')
    py_nodes = asdl.flatten(asdl.ASDLParser().parse(asdl_src))
    print(py_nodes)

    ##

    src_file = os.path.join(os.path.dirname(__file__), 'resolve.py')
    with open(src_file) as f:
        src = f.read()

    root = ast.parse(src, src_file)
    print(root)

    ##

    ast_cls_dct = col.make_map_by(lambda c: c.__name__, lang.deep_subclasses(ast.AST), strict=True)
    ast_poly = msh.Polymorphism(ast.AST, [msh.Impl(ty, tag) for tag, ty in ast_cls_dct.items()])
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(ast_poly)]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(ast_poly)]

    # _attributes = ()
    # _fields = ()


if __name__ == '__main__':
    _main()
