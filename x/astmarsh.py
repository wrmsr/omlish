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
class AsdlNode(lang.Abstract, lang.Sealed):
    name: str
    fields: ta.Sequence[AsdlField] = dc.field(default=(), kw_only=True)
    attributes: ta.Sequence[AsdlField] = dc.field(default=(), kw_only=True)


@dc.dataclass(frozen=True)
class AsdlSum(AsdlNode, lang.Final):
    constructors: ta.Sequence[str] = dc.field(default=(), kw_only=True)


@dc.dataclass(frozen=True)
class AsdlProduct(AsdlNode, lang.Final):
    pass


@dc.dataclass(frozen=True)
class AsdlConstructor(AsdlNode, lang.Final):
    sum: str = dc.field(kw_only=True)


def _main() -> None:
    asdl_src = lang.get_relative_resources(globals=globals())['python-3.12.asdl'].read_bytes().decode('utf-8')
    py_asdl = asdl.ASDLParser().parse(asdl_src)
    print(py_asdl)

    nodes: list[AsdlNode] = []

    def mk_field(af: asdl.Field) -> AsdlField:
        return AsdlField(
            af.name,
            af.type,
            n='*' if af.seq else '?' if af.opt else 1,
        )

    def mk_fields(afs: ta.Iterable[asdl.Field] | None) -> ta.Sequence[AsdlField]:
        return list(map(mk_field, afs or []))

    for ty in py_asdl.dfns:
        v = ty.value

        if isinstance(v, asdl.Sum):
            nodes.append(AsdlSum(
                ty.name,
                attributes=mk_fields(v.attributes),
                constructors=[c.name for c in v.types],
            ))

            for c in v.types:
                nodes.append(AsdlConstructor(
                    c.name,
                    fields=mk_fields(c.fields),
                    sum=ty.name,
                ))

        elif isinstance(v, asdl.Product):
            nodes.append(AsdlProduct(
                ty.name,
                fields=mk_fields(v.fields),
                attributes=mk_fields(v.attributes),
            ))

        else:
            raise TypeError(v)

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
