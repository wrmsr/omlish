# refcycles.py
#
# Best-effort pure-Python reference-cycle detector.
#
# Intended for occasional explicitly-enabled hygiene/debug usage, not hot paths.
#
# Core idea:
#   - Build a directed graph using gc.get_referents().
#   - Find strongly connected components.
#   - Report SCCs with >1 node, plus self-loops.
#
# Useful knobs:
#   - prune_static_definition_objects:
#       remove boring module/class/function/code scaffolding before SCC detection.
#   - drop_cycles_involving_types:
#       still build SCCs normally, but suppress any detected SCC containing a type.
#   - prune_type_nodes:
#       remove type objects before SCC detection. Blunter and less informative than
#       drop_cycles_involving_types.
#
# Caveats:
#   - This only sees the GC traversal graph, not every possible C/internal ref.
#   - Some extension types may be invisible or incomplete if they do not expose correct tp_traverse behavior.
#   - It will find currently reachable cycles, not just uncollectable garbage.
#   - Running it perturbs the object graph somewhat, so treat results as hints.
import collections as col
import dataclasses as dc
import gc
import sys
import types
import typing as ta


##


_ATOMIC_TYPES: tuple[type, ...] = (
    type(None),
    bool,
    int,
    float,
    complex,
    str,
    bytes,
    bytearray,
    range,
)


_BASE_SKIP_TYPES: tuple[type, ...] = (
    types.FrameType,
    types.TracebackType,
)


_STATIC_DESCRIPTOR_TYPES = tuple(
    t
    for t in (
        getattr(types, 'GetSetDescriptorType', None),
        getattr(types, 'MemberDescriptorType', None),
        getattr(types, 'WrapperDescriptorType', None),
        getattr(types, 'MethodDescriptorType', None),
        getattr(types, 'ClassMethodDescriptorType', None),
    )
    if t is not None
)


NodeFilter: ta.TypeAlias = ta.Callable[[object], bool]
EdgeFilter: ta.TypeAlias = ta.Callable[[object, object], bool]
CycleSuppressor: ta.TypeAlias = ta.Callable[
    [tuple[object, ...], tuple[tuple[int, int], ...]],
    bool,
]


@dc.dataclass(frozen=True)
class ObjInfo:
    oid: int
    typ: str
    generic_repr: str


@dc.dataclass(frozen=True)
class CycleInfo:
    objects: tuple[ObjInfo, ...]
    edges: tuple[tuple[int, int], ...]


@dc.dataclass(frozen=True)
class CycleScanResult:
    cycles: tuple[CycleInfo, ...]
    total_cycles_seen: int
    suppressed_type_cycles: int = 0
    suppressed_other_cycles: int = 0
    truncated: bool = False


def _type_name(obj: object) -> str:
    t = type(obj)
    return f'{t.__module__}.{t.__qualname__}'


def _generic_repr(obj: object) -> str:
    """
    Avoid running user-defined __repr__.

    This gives less useful output for builtin containers, but avoids arbitrary code execution while reporting.
    """

    try:
        return object.__repr__(obj)
    except Exception as e:  # pragma: no cover
        return f'<repr failed: {type(e).__name__}: {e}>'


def _obj_info(obj: object) -> ObjInfo:
    return ObjInfo(
        oid=id(obj),
        typ=_type_name(obj),
        generic_repr=_generic_repr(obj),
    )


def _is_atomic(obj: object) -> bool:
    return isinstance(obj, _ATOMIC_TYPES)


def _is_base_skipped(obj: object) -> bool:
    return isinstance(obj, _BASE_SKIP_TYPES)


def default_node_filter(obj: object) -> bool:
    """
    Conservative default node filter.

    This excludes obvious atomics and live execution machinery, but does not exclude modules, classes, functions, etc.
    Use prune_static_definition_objects=True for that.
    """

    if _is_atomic(obj):
        return False

    if _is_base_skipped(obj):
        return False

    return gc.is_tracked(obj)


def default_edge_filter(src: object, dst: object) -> bool:
    del src

    return default_node_filter(dst)


def make_static_object_filter() -> NodeFilter:
    """
    Return predicate: obj -> True if obj appears to be boring static definition machinery.

    This is intentionally heuristic.

    It suppresses the common giant SCCs shaped like:

        module globals dict
          -> class
          -> class dict
          -> method function
          -> function.__globals__
          -> module globals dict

    It deliberately does NOT suppress:
      - bound methods
      - closure functions
      - closure cells
      - normal instances

    because those often represent hygiene-relevant cycles.
    """

    static_dict_ids: set[int] = set()

    # Module globals dicts.
    for mod in list(sys.modules.values()):
        d = getattr(mod, '__dict__', None)
        if isinstance(d, dict):
            static_dict_ids.add(id(d))

    # Class/type dictionaries.
    #
    # type.__dict__ exposes a mappingproxy, but gc.get_referents(type_obj) usually exposes the underlying dict.
    for obj in gc.get_objects():
        if isinstance(obj, type):
            for ref in gc.get_referents(obj):
                if isinstance(ref, dict):
                    static_dict_ids.add(id(ref))

    def is_static_function(fn: object) -> bool:
        if not isinstance(fn, types.FunctionType):
            return False

        # Closure functions are often dynamic and hygiene-relevant:
        #
        #   self.fn = lambda: self
        #
        # creates self -> fn -> closure cell -> self.
        if fn.__closure__ is not None:
            return False

        # Nested functions are more likely to be dynamically created.
        if '<locals>' in fn.__qualname__:
            return False

        return True

    def is_static(obj: object) -> bool:
        if id(obj) in static_dict_ids:
            return True

        if isinstance(obj, types.ModuleType):
            return True

        if isinstance(obj, type):
            return True

        if is_static_function(obj):
            return True

        if isinstance(obj, types.CodeType):
            return True

        if isinstance(obj, types.MappingProxyType):
            return True

        if isinstance(obj, _STATIC_DESCRIPTOR_TYPES):
            return True

        if isinstance(obj, (types.BuiltinFunctionType, types.BuiltinMethodType)):
            return True

        return False

    return is_static


def _compose_filters(
    *,
    node_filter: NodeFilter,
    edge_filter: EdgeFilter,
    prune_static_definition_objects: bool,
    prune_type_nodes: bool,
) -> tuple[NodeFilter, EdgeFilter]:
    static_filter = (
        make_static_object_filter()
        if prune_static_definition_objects
        else None
    )

    def effective_node_filter(obj: object) -> bool:
        if prune_type_nodes and isinstance(obj, type):
            return False

        if static_filter is not None and static_filter(obj):
            return False

        return node_filter(obj)

    def effective_edge_filter(src: object, dst: object) -> bool:
        if not effective_node_filter(dst):
            return False

        return edge_filter(src, dst)

    return effective_node_filter, effective_edge_filter


def _reachable_from(
    seeds: ta.Iterable[object],
    *,
    max_depth: int,
    max_nodes: int,
    node_filter: NodeFilter,
    edge_filter: EdgeFilter,
) -> dict[int, object]:
    seen: dict[int, object] = {}
    q: col.deque[tuple[object, int]] = col.deque((s, 0) for s in seeds)

    while q and len(seen) < max_nodes:
        obj, depth = q.popleft()
        oid = id(obj)

        if oid in seen:
            continue

        if not node_filter(obj):
            continue

        seen[oid] = obj

        if depth >= max_depth:
            continue

        for child in gc.get_referents(obj):
            if edge_filter(obj, child):
                q.append((child, depth + 1))

    return seen


def _snapshot_all_tracked(
    *,
    max_nodes: int,
    node_filter: NodeFilter,
) -> dict[int, object]:
    out: dict[int, object] = {}

    for obj in gc.get_objects():
        if len(out) >= max_nodes:
            break

        if node_filter(obj):
            out[id(obj)] = obj

    return out


def _dedupe_preserving_order(xs: ta.Iterable[int]) -> tuple[int, ...]:
    seen: set[int] = set()
    out: list[int] = []

    for x in xs:
        if x in seen:
            continue

        seen.add(x)
        out.append(x)

    return tuple(out)


def _build_graph(
    id_to_obj: dict[int, object],
    *,
    edge_filter: EdgeFilter,
) -> dict[int, tuple[int, ...]]:
    allowed = set(id_to_obj)
    graph: dict[int, tuple[int, ...]] = {}

    for oid, obj in id_to_obj.items():
        dsts: list[int] = []

        for child in gc.get_referents(obj):
            cid = id(child)

            if cid not in allowed:
                continue

            if not edge_filter(obj, child):
                continue

            dsts.append(cid)

        graph[oid] = _dedupe_preserving_order(dsts)

    return graph


def _tarjan_sccs(graph: dict[int, tuple[int, ...]]) -> list[tuple[int, ...]]:
    index = 0
    stack: list[int] = []
    on_stack: set[int] = set()
    indices: dict[int, int] = {}
    lowlinks: dict[int, int] = {}
    comps: list[tuple[int, ...]] = []

    def strong_connect(v: int) -> None:
        nonlocal index

        indices[v] = index
        lowlinks[v] = index
        index += 1

        stack.append(v)
        on_stack.add(v)

        for w in graph.get(v, ()):
            if w not in indices:
                strong_connect(w)
                lowlinks[v] = min(lowlinks[v], lowlinks[w])
            elif w in on_stack:
                lowlinks[v] = min(lowlinks[v], indices[w])

        if lowlinks[v] == indices[v]:
            comp: list[int] = []

            while True:
                w = stack.pop()
                on_stack.remove(w)
                comp.append(w)

                if w == v:
                    break

            comps.append(tuple(comp))

    for v in graph:
        if v not in indices:
            strong_connect(v)

    return comps


def _is_cycle_component(
    comp: tuple[int, ...],
    graph: dict[int, tuple[int, ...]],
) -> bool:
    if len(comp) > 1:
        return True

    v = comp[0]
    return v in graph.get(v, ())


def find_reference_cycles(
    seeds: ta.Iterable[object] | None = None,
    *,
    collect_first: bool = True,
    max_depth: int = 25,
    max_nodes: int = 100_000,
    max_reported_cycles: int = 100,
    node_filter: NodeFilter = default_node_filter,
    edge_filter: EdgeFilter = default_edge_filter,
    prune_static_definition_objects: bool = False,
    prune_type_nodes: bool = False,
    drop_cycles_involving_types: bool = False,
    cycle_suppressor: CycleSuppressor | None = None,
) -> CycleScanResult:
    """
    Find best-effort reference cycles.

    If seeds is None:
        scan a snapshot of all GC-tracked objects.

    If seeds is provided:
        traverse outward from those seed objects.

    prune_static_definition_objects:
        Exclude modules, types/classes, module globals dicts, class dicts, mappingproxy objects, code objects,
        non-closure module/class functions, static descriptors, and builtin function/method objects before building the
        SCC graph.

    prune_type_nodes:
        Exclude type objects before building the SCC graph.

    drop_cycles_involving_types:
        Build the graph normally, detect SCCs normally, but suppress any resulting cycle containing a type object. This
        is usually preferable to prune_type_nodes if you want honest accounting.

    cycle_suppressor:
        Optional predicate called with raw objects and intra-cycle id edges. Return True to suppress that cycle.

    Note:
        If prune_static_definition_objects=True, most type-involving cycles will already be removed before
        drop_cycles_involving_types gets a chance to count them.
    """

    if collect_first:
        gc.collect()

    effective_node_filter, effective_edge_filter = _compose_filters(
        node_filter=node_filter,
        edge_filter=edge_filter,
        prune_static_definition_objects=prune_static_definition_objects,
        prune_type_nodes=prune_type_nodes,
    )

    if seeds is None:
        id_to_obj = _snapshot_all_tracked(
            max_nodes=max_nodes,
            node_filter=effective_node_filter,
        )
    else:
        id_to_obj = _reachable_from(
            seeds,
            max_depth=max_depth,
            max_nodes=max_nodes,
            node_filter=effective_node_filter,
            edge_filter=effective_edge_filter,
        )

    graph = _build_graph(id_to_obj, edge_filter=effective_edge_filter)

    cycles: list[CycleInfo] = []
    total_cycles_seen = 0
    suppressed_type_cycles = 0
    suppressed_other_cycles = 0
    truncated = False

    for comp in _tarjan_sccs(graph):
        if not _is_cycle_component(comp, graph):
            continue

        total_cycles_seen += 1

        comp_set = set(comp)

        edges = tuple(
            (src, dst)
            for src in comp
            for dst in graph.get(src, ())
            if dst in comp_set
        )

        objs = tuple(id_to_obj[oid] for oid in comp)

        if drop_cycles_involving_types and any(isinstance(obj, type) for obj in objs):
            suppressed_type_cycles += 1
            continue

        if cycle_suppressor is not None and cycle_suppressor(objs, edges):
            suppressed_other_cycles += 1
            continue

        if len(cycles) >= max_reported_cycles:
            truncated = True
            continue

        cycles.append(
            CycleInfo(
                objects=tuple(_obj_info(obj) for obj in objs),
                edges=edges,
            ),
        )

    return CycleScanResult(
        cycles=tuple(cycles),
        total_cycles_seen=total_cycles_seen,
        suppressed_type_cycles=suppressed_type_cycles,
        suppressed_other_cycles=suppressed_other_cycles,
        truncated=truncated,
    )


def format_cycle(cycle: CycleInfo, *, max_objects: int = 50) -> str:
    lines: list[str] = []

    lines.append(f'cycle with {len(cycle.objects)} objects, {len(cycle.edges)} edges:')

    shown = cycle.objects[:max_objects]

    for obj in shown:
        lines.append(f'  {obj.oid:#x} {obj.typ} {obj.generic_repr}')

    if len(cycle.objects) > len(shown):
        lines.append(f'  ... {len(cycle.objects) - len(shown)} more objects')

    if cycle.edges:
        lines.append('  edges:')

        for src, dst in cycle.edges[:max_objects]:
            lines.append(f'    {src:#x} -> {dst:#x}')

        if len(cycle.edges) > max_objects:
            lines.append(f'    ... {len(cycle.edges) - max_objects} more edges')

    return '\n'.join(lines)


def format_scan_result(
    result: CycleScanResult,
    *,
    max_cycles: int = 20,
    max_objects_per_cycle: int = 50,
) -> str:
    lines: list[str] = []

    lines.append(f'reported cycles: {len(result.cycles)}')
    lines.append(f'total cycles seen: {result.total_cycles_seen}')
    lines.append(f'suppressed type cycles: {result.suppressed_type_cycles}')
    lines.append(f'suppressed other cycles: {result.suppressed_other_cycles}')
    lines.append(f'truncated: {result.truncated}')

    for i, cycle in enumerate(result.cycles[:max_cycles], 1):
        lines.append('')
        lines.append(f'#{i}')
        lines.append(format_cycle(cycle, max_objects=max_objects_per_cycle))

    if len(result.cycles) > max_cycles:
        lines.append('')
        lines.append(f'... {len(result.cycles) - max_cycles} more reported cycles')

    return '\n'.join(lines)


def collect_unreachable_with_saveall() -> list[object]:
    """
    Debug helper for unreachable garbage specifically.

    This temporarily enables DEBUG_SAVEALL, runs a collection, copies gc.garbage, clears gc.garbage, and restores the
    old debug flags.

    Objects returned from this function are now strongly referenced by the returned list.
    """

    old_debug = gc.get_debug()

    try:
        gc.set_debug(old_debug | gc.DEBUG_SAVEALL)
        gc.collect()
        out = list(gc.garbage)
        gc.garbage.clear()
        return out
    finally:
        gc.set_debug(old_debug)


if __name__ == '__main__':
    class A:
        pass

    a = A()
    b = A()

    a.other = b
    b.other = a

    result = find_reference_cycles(
        seeds=[a],
        max_depth=10,
        drop_cycles_involving_types=True,
    )

    print(format_scan_result(result))
