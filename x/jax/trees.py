import dataclasses as dc
import itertools as it
import typing as ta

from .utils import unzip2


def flatten_fun(f, in_tree):
    store = Store()

    def flat_fun(*args_flat):
        pytree_args = tree_unflatten(in_tree, args_flat)
        out = f(*pytree_args)
        out_flat, out_tree = tree_flatten(out)
        store.set_value(out_tree)
        return out_flat

    return flat_fun, store


class Empty:
    pass


empty = Empty()


class Store:
    val = empty

    def set_value(self, val):
        assert self.val is empty
        self.val = val

    def __call__(self):
        return self.val


@dc.dataclass(frozen=True)
class NodeType:
    name: str
    to_iterable: ta.Callable
    from_iterable: ta.Callable


def register_pytree_node(ty: ta.Type, to_iter: ta.Callable, from_iter: ta.Callable) -> None:
    node_types[ty] = NodeType(str(ty), to_iter, from_iter)


node_types: ta.Dict[ta.Type, NodeType] = {}
register_pytree_node(tuple, lambda t: (None, t), lambda _, xs: tuple(xs))
register_pytree_node(list, lambda l: (None, l), lambda _, xs: list(xs))
register_pytree_node(dict, lambda d: map(tuple, unzip2(sorted(d.items()))), lambda keys, vals: dict(zip(keys, vals)))


@dc.dataclass(frozen=True)
class PyTreeDef:
    node_type: NodeType
    node_metadata: ta.Hashable
    child_treedefs: ta.Tuple['PyTreeDef', ...]


class Leaf:
    pass


leaf = Leaf()


def tree_flatten(x: ta.Any) -> ta.Tuple[ta.List[ta.Any], PyTreeDef]:
    children_iter, treedef = _tree_flatten(x)
    return list(children_iter), treedef


def _tree_flatten(x: ta.Any) -> ta.Tuple[ta.Iterable, PyTreeDef]:
    node_type = node_types.get(type(x))
    if node_type:
        node_metadata, children = node_type.to_iterable(x)
        children_flat, child_trees = unzip2(map(_tree_flatten, children))
        flattened = it.chain.from_iterable(children_flat)
        return flattened, PyTreeDef(node_type, node_metadata, tuple(child_trees))
    else:
        return [x], leaf


def tree_unflatten(treedef: PyTreeDef, xs: ta.List[ta.Any]) -> ta.Any:
    return _tree_unflatten(treedef, iter(xs))


def _tree_unflatten(treedef: PyTreeDef, xs: ta.Iterator) -> ta.Any:
    if treedef is leaf:
        return next(xs)
    else:
        children = (_tree_unflatten(t, xs) for t in treedef.child_treedefs)
        return treedef.node_type.from_iterable(treedef.node_metadata, children)
