"""
TODO:
 - strip/readd date/ds clamps
  - https://docs.snowflake.com/en/user-guide/tables-clustering-keys.html
  - https://docs.snowflake.com/en/sql-reference/sql/create-table.html#syntax
 - *name disambiguator* (powered by sym res)
 - expression inversion / undo queries
 - selectallexpansion
 - symbol resolution / namification
 - inlining
  - upstreams
  - (mat)views
  - table funcs (strats: laterals? subqueries? ctes?)
 - jinja eval
 - parameter eval
 - lint / bugsquash
 - opto opportunities
 - window granularity
  - can you compute x days of a daily query with a single query with correct results (enforce agg bounds)
 - optimizations
  - pushdown
  - drop unused rels, cols
 - name mangling
 - limits (limit 0) pushdown
 - integrity check gen?
 - pk / ds? / 'generic?' propagation?
 - omni.matching?

dialect extensions:
 - intrin fns
  - let forms
  - lool jmespath
   - can use udfs too
   - can jit udfs too
   - 'by default search gets whole row'
   - by default embed in iceworm-jvm and webpack js for sf
  - drop - drops a col
 - haskell like lang extensions lol - no obv, all or nothing
 - $var injection? yaml consts and shit? dont need $ds and that trash, reduced importance
 - crazy object space equiv?
  - if no struct type, use table types? array of objs as tbl lol, table scalars
  - as sf does variant/object, large benefit is type awareness of fields
   - when extracting and unnesting and shoving in a table know the col types
   - oof, snowflake DOES NOT ENFORCE OBJECT SHAPES - WOULD HAVE TO BE PREPARED TO GET RANDOM SHIT
  - intrin != special - intrin is blackbox macro, special is a whole analysis/xform concept
 - lambdas? https://prestodb.io/blog/2020/03/02/presto-lambda
 - allow trailing commas, where ‘ands’ (really in parsing layer)
"""
import collections  # noqa
import typing as ta

from omnibus import check
from omnibus import code as ocode
from omnibus import dataclasses as dc
from omnibus import dispatch
from omnibus import lang

from . import analysis as ana  # noqa
from . import nodes as no
from .. import metadata as md
from ..types import QualifiedName


class Origin(lang.Marker):
    pass


class Transformer(dispatch.Class, lang.Abstract):
    __call__ = dispatch.property()

    def __call__(self, node: no.Node, **kwargs) -> no.Node:  # noqa
        res = node.map(self, **kwargs)
        return dc.replace(res, meta={**res.meta, Origin: node})


@dc.dataclass(frozen=True)
class ReplaceNamesTransformer(Transformer):
    dct: ta.Mapping[QualifiedName, QualifiedName]

    def __call__(self, node: no.QualifiedNameNode) -> no.QualifiedNameNode:  # noqa
        try:
            repl = self.dct[node.name]
        except KeyError:
            return node
        else:
            return no.QualifiedNameNode.of(repl)


def replace_names(node: no.Node, dct: ta.Mapping[QualifiedName, QualifiedName]) -> no.Node:
    return ReplaceNamesTransformer(dct)(node)


class AliasRelationsTransformer(Transformer):

    def __init__(self, root: no.Node) -> None:
        super().__init__()

        self._root = check.isinstance(root, no.Node)

        self._basic = ana.basic(root)
        self._pna = ana.PreferredNameAnalyzer()

        rel_names = set()
        for ar in self._basic.get_node_type_set(no.AliasedRelation):
            rel_names.add(ar.alias.name)
        for tbl in self._basic.get_node_type_set(no.Table):
            rel_names.add(tbl.name.parts[-1].name)
        self._name_gen = ocode.name_generator(unavailable_names=rel_names)

    def __call__(self, node: no.AliasedRelation) -> no.Node:  # noqa
        return super().__call__(node)

    def __call__(self, node: no.Relation) -> no.Node:  # noqa
        parent = self._basic.parents_by_node[node]
        node = super().__call__(node)
        if not isinstance(parent, no.AliasedRelation):
            if isinstance(node, no.Table):
                name = node.name.parts[-1].name  # FIXME: lame
            else:
                name = self._name_gen()
            node = no.AliasedRelation(
                node,
                no.Identifier(name))
        return node


class ExpandSelectsTransformer(Transformer):

    def __init__(self, root: no.Node, catalog: md.Catalog) -> None:
        super().__init__()

        self._root = check.isinstance(root, no.Node)
        self._catalog = check.isinstance(catalog, md.Catalog)

    def __call__(self, node: no.Select) -> no.Node:  # noqa
        sup = super().__call__
        rels = [check.isinstance(sup(r), no.Relation) for r in node.relations]

        items = []
        for item in node.items:
            if isinstance(item, no.AllSelectItem):
                def rec(rel: no.Relation, alias: ta.Optional[str] = None) -> None:
                    if isinstance(rel, no.Table):
                        tbl = self._catalog.tables_by_name[rel.name.name]
                        for col in tbl.columns:
                            items.append(
                                no.ExprSelectItem(
                                    no.QualifiedNameNode.of([alias or tbl.name, col.name])))

                    elif isinstance(rel, no.AliasedRelation):
                        check.none(alias)
                        rec(rel.relation, rel.alias.name)

                    else:
                        raise TypeError(rel)

                for rel in rels:
                    rec(rel)

            elif isinstance(item, no.IdentifierAllSelectItem):
                raise NotImplementedError

            elif isinstance(item, no.ExprSelectItem):
                items.append(self(item))

            else:
                raise TypeError(item)

        return super().__call__(node, items=items, relations=rels)


class LabelSelectItemsTransformer(Transformer):

    def __init__(self, root: no.Node) -> None:
        super().__init__()

        self._root = check.isinstance(root, no.Node)

        self._basic = ana.basic(root)
        self._pna = ana.PreferredNameAnalyzer()

        labels = set()
        for item in self._basic.get_node_type_set(no.ExprSelectItem):
            if item.label is not None:
                labels.add(check.not_none(item.label).name)
        self._name_gen = ocode.name_generator(unavailable_names=labels)

    def __call__(self, node: no.AllSelectItem) -> no.Node:  # noqa
        raise TypeError(node)

    def __call__(self, node: no.Select) -> no.Node:  # noqa
        sup = super().__call__
        items_and_names = [
            (item, self._pna(item))
            for item in node.items
            for item in [sup(check.isinstance(item, no.ExprSelectItem))]
        ]

        cts = collections.Counter()
        for item, name in items_and_names:
            cts[name] += 1

        new_items = []
        rem = {n: -c for n, c in cts.items()}
        for item, name in items_and_names:
            item = check.isinstance(item, no.ExprSelectItem)
            if cts[name] == 1:
                check.state(rem[name] == -1)
                rem[name] = 0
                if name is not None:
                    new_name = name
                else:
                    new_name = self._name_gen()
            else:
                rct = -rem[name]
                check.state(rct)
                rem[name] += 1
                new_name = f'{name}_{rct}'  # FIXME: conflict-free via _name_gen

            if item.label:
                check.state(item.label.name == new_name)
                new_item = item
            else:
                new_item = no.ExprSelectItem(item.value, no.Identifier(new_name))

            new_items.append(new_item)

        check.state(rem == {k: 0 for k in cts})

        return super().__call__(node, items=new_items)


class CteHoistTransformer(Transformer):
    pass
