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
from .. import lang


T = ta.TypeVar('T')


##


class LinkError(KeyError):
    pass


def traverse_links(
        links: ta.Mapping[T, ta.Iterable[T]],
        roots: ta.Iterable[T],
        *,
        include_roots: bool = False,
        strict: bool = False,
) -> set[T]:
    """Returns all keys deeply reachable from given roots. Handles cycles."""

    roots = set(roots)

    todo = set(roots)
    seen: set[T] = set()
    while todo:
        key = todo.pop()
        seen.add(key)

        try:
            cur = links[key]
        except KeyError:
            if strict:
                raise LinkError(key) from None
        else:
            todo.update(set(cur) - seen)

    if include_roots:
        return seen
    else:
        return seen - roots


def invert_links(
        links: ta.Mapping[T, ta.Iterable[T]],
        *,
        auto_add_roots: bool = False,
        if_absent: ta.Literal['raise', 'ignore', 'add'] = 'add',
) -> dict[T, set[T]]:
    check.in_(if_absent, ('raise', 'ignore', 'add'))
    if if_absent != 'add':
        check.arg(auto_add_roots, 'auto_add_roots must be True with given if_absent is not "add"')

    ret: dict[T, set[T]]
    if auto_add_roots:
        ret = {src: set() for src in links}
    else:
        ret = {}

    for src, dsts in links.items():
        for dst in dsts:
            try:
                tgt = ret[dst]
            except KeyError:
                if if_absent == 'raise':
                    raise LinkError(dst) from None
                elif if_absent == 'ignore':
                    continue
                elif if_absent == 'add':
                    tgt = ret[dst] = set()
                else:
                    raise RuntimeError from None

            tgt.add(src)

    return ret


##


class Dag(ta.Generic[T]):
    """Given 'input_its_by_outputs', or a map from nodes to that node's dependencies."""

    def __init__(
            self,
            input_its_by_outputs: ta.Mapping[T, ta.Iterable[T]],
            *,
            auto_add_outputs: bool = True,
            if_absent: ta.Literal['raise', 'ignore', 'add'] = 'add',
    ) -> None:
        super().__init__()

        self._input_sets_by_output = {u: set(d) for u, d in input_its_by_outputs.items()}

        self._output_sets_by_input = invert_links(
            self._input_sets_by_output,
            auto_add_roots=auto_add_outputs,
            if_absent=if_absent,
        )

    @property
    def input_sets_by_output(self) -> ta.Mapping[T, ta.AbstractSet[T]]:
        return self._input_sets_by_output

    @property
    def output_sets_by_input(self) -> ta.Mapping[T, ta.AbstractSet[T]]:
        return self._output_sets_by_input

    def subdag(
            self,
            roots: ta.Iterable[T],
            *,
            ignored: ta.Iterable[T] | None = None,
    ) -> 'Subdag[T]':
        return Subdag(
            self,
            roots,
            ignored=ignored,
        )


class Subdag(ta.Generic[T]):
    def __init__(
            self,
            dag: Dag[T],
            roots: ta.Iterable[T],
            *,
            ignored: ta.Iterable[T] | None = None,
    ) -> None:
        super().__init__()

        self._dag: Dag[T] = check.isinstance(dag, Dag)
        self._roots = set(roots)
        self._ignored = set(ignored or []) - self._roots

    @property
    def dag(self) -> Dag[T]:
        return self._dag

    @property
    def roots(self) -> ta.AbstractSet[T]:
        return self._roots

    @property
    def ignored(self) -> ta.AbstractSet[T]:
        return self._ignored

    @lang.cached_property
    def inputs(self) -> ta.AbstractSet[T]:
        return traverse_links(self._dag.input_sets_by_output, self._roots) - self._ignored

    @lang.cached_property
    def outputs(self) -> ta.AbstractSet[T]:
        return traverse_links(self._dag.output_sets_by_input, self._roots) - self._ignored

    @lang.cached_property
    def output_inputs(self) -> ta.AbstractSet[T]:
        return traverse_links(self._dag.input_sets_by_output, self.outputs) - self._ignored

    @lang.cached_property
    def all(self) -> ta.AbstractSet[T]:
        return self.roots | self.inputs | self.outputs | self.output_inputs
