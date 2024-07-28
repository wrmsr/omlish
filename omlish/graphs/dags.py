"""
TODO:
 - parser?
 - js? viz.js, d3, visjs
 - cycle detection
 - networkx adapter
 - https://docs.python.org/3.9/library/graphlib.html#module-graphlib
"""
import typing as ta

from .. import check
from .. import collections as col
from .. import lang


K = ta.TypeVar('K')
V = ta.TypeVar('V')
T = ta.TypeVar('T')
U = ta.TypeVar('U')


def traverse_links(data: ta.Mapping[T, ta.Iterable[T]], keys: ta.Iterable[T]) -> ta.Set[T]:
    keys = set(keys)
    todo = set(keys)
    seen: ta.Set[T] = set()
    while todo:
        key = todo.pop()
        seen.add(key)
        cur = data.get(key, [])
        todo.update(set(cur) - seen)
    return seen - keys


def invert_set_map(src: ta.Mapping[K, ta.Iterable[V]], *, symmetric: bool = False) -> ta.Dict[V, ta.Set[K]]:
    dst: ta.Dict[V, ta.Set[K]]
    if symmetric:
        dst = {ta.cast(V, l): set() for l in src}
    else:
        dst = {}
    for l, rs in src.items():
        for r in rs:
            dst.setdefault(r, set()).add(l)
    return dst


class Dag(ta.Generic[T]):

    def __init__(self, input_its_by_outputs: ta.Mapping[T, ta.Iterable[T]]) -> None:
        super().__init__()

        self._input_sets_by_output = {u: set(d) for u, d in input_its_by_outputs.items()}

    @property
    def input_sets_by_output(self) -> ta.Mapping[T, ta.AbstractSet[T]]:
        return self._input_sets_by_output

    @lang.cached_property
    def output_sets_by_input(self) -> ta.Mapping[T, ta.AbstractSet[T]]:
        return col.invert_set_map(self._input_sets_by_output, symmetric=True)

    def subdag(self, *args, **kwargs) -> 'Dag.Subdag[T]':
        return self.Subdag(self, *args, **kwargs)

    class Subdag(ta.Generic[U]):

        def __init__(
                self,
                dag: 'Dag[U]',
                targets: ta.Iterable[U],
                *,
                ignored: ta.Optional[ta.Iterable[U]] = None,
        ) -> None:
            super().__init__()

            self._dag = check.isinstance(dag, Dag)
            self._targets = set(targets)
            self._ignored = set(ignored or []) - self._targets

        @property
        def dag(self) -> 'Dag[U]':
            return self._dag

        @property
        def targets(self) -> ta.AbstractSet[U]:
            return self._targets

        @property
        def ignored(self) -> ta.AbstractSet[U]:
            return self._ignored

        @lang.cached_property
        def inputs(self) -> ta.AbstractSet[U]:
            return col.traverse_links(self.dag.input_sets_by_output, self.targets) - self.ignored

        @lang.cached_property
        def outputs(self) -> ta.AbstractSet[U]:
            return col.traverse_links(self.dag.output_sets_by_input, self.targets) - self.ignored

        @lang.cached_property
        def output_inputs(self) -> ta.AbstractSet[U]:
            return col.traverse_links(self.dag.input_sets_by_output, self.outputs) - self.ignored

        @lang.cached_property
        def all(self) -> ta.AbstractSet[U]:
            return self.targets | self.inputs | self.outputs | self.output_inputs
