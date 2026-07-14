"""
Native recursive alias support: `type` statement aliases reflect to recursive TypeAliasType nodes, unwrap through
TypeAliasMarshalerFactory, and terminate through the type cache + recursive proxy - no ReflectOverride needed.
"""
import typing as ta

from ... import dataclasses as dc
from ... import marshal as msh


type StrTree = ta.Mapping[str, StrTree] | str

type IntListTree = ta.Sequence[IntListTree] | int


@dc.dataclass(frozen=True)
class TreeNode:
    name: str
    children: ta.Sequence['TreeNode'] = ()  # noqa


def test_recursive_mapping_alias():
    v: ta.Any = {'a': {'b': 'c', 'd': {'e': 'f'}}, 'g': 'h'}
    m = msh.marshal(v, StrTree)
    assert m == v
    u = msh.unmarshal(m, StrTree)
    assert u == v


def test_recursive_sequence_alias():
    v: ta.Any = [1, [2, [3, 4], 5], 6]
    m = msh.marshal(v, IntListTree)
    assert m == v
    u = msh.unmarshal(m, IntListTree)
    assert u == (1, (2, (3, 4), 5), 6)


def test_recursive_dataclass():
    v = TreeNode('root', [TreeNode('left', [TreeNode('leaf')]), TreeNode('right')])
    m = msh.marshal(v)
    assert m == {
        'name': 'root',
        'children': [
            {'name': 'left', 'children': [{'name': 'leaf', 'children': []}]},
            {'name': 'right', 'children': []},
        ],
    }
    u = msh.unmarshal(m, TreeNode)
    assert u == TreeNode('root', (TreeNode('left', (TreeNode('leaf'),)), TreeNode('right')))


def test_nonrecursive_alias():
    type Ints = ta.Sequence[int]

    m = msh.marshal([1, 2, 3], Ints)
    assert m == [1, 2, 3]
    assert msh.unmarshal(m, Ints) == (1, 2, 3)
