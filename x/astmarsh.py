"""
TODO:
 - marshal 'external object... infos?'
 - gen map from ast node name -> map from field name to field type
"""
import ast
import dataclasses as dc
import os.path
import typing as ta

from omlish import collections as col
from omlish import lang
from omlish import marshal as msh

from . import asdl


@dc.dataclass(frozen=True)
class AsdlField:
    name: str
    type: str
    n: ta.Literal[1, '?', '*'] = 1


@dc.dataclass(frozen=True)
class AsdlNode(lang.Abstract):
    name: str
    attrs: ta.Sequence[AsdlField] = ()
    field: ta.Sequence[AsdlField] = ()


@dc.dataclass(frozen=True)
class AsdlSum(AsdlNode):
    ctors: ta.Sequence[str] = ()


@dc.dataclass(frozen=True)
class AsdlProduct(AsdlNode):
    pass


@dc.dataclass(frozen=True)
class AsdlConstructor(AsdlNode):
    sum: str = dc.field(kw_only=True)


def _main() -> None:
    asdl_src = lang.get_relative_resources(globals=globals())['python-3.12.asdl'].read_bytes().decode('utf-8')
    py_asdl = asdl.ASDLParser().parse(asdl_src)
    print(py_asdl)

    dct: dict[str, AsdlNode] = {}

    def mk_field(af: asdl.Field) -> AsdlField:
        return AsdlField(
            af.name,
            af.type,
            '*' if af.seq else '?' if af.opt else 1,
        )

    for ty in py_asdl.dfns:
        v = ty.value

        if isinstance(v, asdl.Sum):
            dct[ty.name] = AsdlSum(
                ty.name,


            )

            print(f'sum: {ty.name}')
            for a in v.attributes or ():
                print(f'a: {a.name}')

            for c in v.types:
                print()
                print(f'ctor: {c.name}')
                for f in c.fields or ():
                    print(f'f: {f.name}')

        elif isinstance(v, asdl.Product):
            print(f'prod: {ty.name}')
            for f in v.fields or ():
                print(f'f: {f.name}')
            for a in v.attributes or ():
                print(f'a: {a.name}')

        else:
            raise TypeError(v)

        print()

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
