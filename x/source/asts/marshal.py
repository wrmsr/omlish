"""
TODO:
 - marshal 'external object... infos?'
 - gen map from ast node name -> map from field name to field type
"""
import ast
import typing as ta

from omlish import collections as col
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl
from omlish.formats import json

from omlish.text import asdl


##


def _main() -> None:
    asdl_src = lang.get_relative_resources('grammars', globals=globals())['python-3.12.asdl'].read_bytes().decode('utf-8')
    py_nodes = asdl.flatten(asdl.AsdlParser().parse(asdl_src))
    py_node_fields = asdl.build_fields_info(py_nodes)

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

    ##

    def mk_fld_ty(ft: str, fa: asdl.FlatFieldArity) -> rfl.Type:
        if ft in ast_cls_dct:
            # ty = ast_cls_dct[ft]
            ty = ast.AST
        else:
            ty = {
                'identifier': str,
                'string': str,
                'int': int,
                'constant': ta.Any,
            }[ft]

        if fa == 1:
            return ty
        elif fa == '*':
            return ta.List[ty]
        elif fa == '?':
            return ta.Optional[ty]
        else:
            raise ValueError(fa)  # noqa

    msh_dct = {}
    for c in ast_cls_lst:
        msh_dct[c] = [
            msh.FieldInfo(
                name=fn,
                type=mk_fld_ty(ft, fa),
                marshal_name=fn,
                unmarshal_names=[fn],
            )
            for fn, (ft, fa) in py_node_fields.get(c.__name__, {}).items()
        ]

    ##

    ast_poly = msh.Polymorphism(ast.AST, [msh.Impl(ty, tag) for tag, ty in ast_cls_dct.items()])

    msh.install_standard_factories(
        msh.PolymorphismMarshalerFactory(ast_poly),
        msh.SimpleObjectMarshalerFactory(msh_dct),

        msh.PolymorphismUnmarshalerFactory(ast_poly),
        msh.SimpleObjectUnmarshalerFactory(msh_dct),
    )

    ##

    src_file = __file__
    with open(src_file) as f:
        src = f.read()

    root = ast.parse(src, src_file)

    ##

    root_j = json.dumps_pretty(msh.marshal(root, ast.AST))
    print(root_j)

    ##

    u_root = msh.unmarshal(json.loads(root_j), ast.AST)
    print(u_root)

    ##

    out_src = ast.unparse(u_root)
    print(out_src)


if __name__ == '__main__':
    _main()
