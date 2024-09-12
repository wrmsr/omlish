"""
https://github.com/wylee/Dijkstar/blob/75d7baad97b3ab6f1b43bd676a2b34586d74f510/src/dijkstar/algorithm.py
"""
# Copyright (c) 2021 Wyatt Baldwin <self@wyattbaldwin.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import collections
import heapq
import itertools
import math
import typing as ta

import pytest


Graph: ta.TypeAlias = dict


PathInfo = collections.namedtuple("PathInfo", ("nodes", "edges", "costs", "total_cost"))
DebugInfo = collections.namedtuple("DebugInfo", "costs visited")


class DijkstarError(Exception):
    pass


class NoPathError(DijkstarError):
    pass


def find_path(
        graph,
        s,
        d,
        annex=None,
        cost_func=None,
        heuristic_func=None,
) -> PathInfo:
    predecessors = single_source_shortest_paths(graph, s, d, annex, cost_func, heuristic_func)
    return extract_shortest_path_from_predecessor_list(predecessors, d)


def single_source_shortest_paths(
        graph,
        s,
        d=None,
        annex=None,
        cost_func=None,
        heuristic_func=None,
        debug=False
):
    """Find path from node ``s`` to all other nodes or just to ``d``.

    ``graph``
        An adjacency list that's structured as a dict of dicts (see
        :class:`dijkstra.graph.Graph`). Other than the structure, no
        other assumptions are made about the types of the nodes or edges
        in the graph. If ``cost_func`` isn't specified, edges will be
        assumed to be values that can be compared directly (e.g.,
        numbers, or any other comparable type).

    ``s``
        Start node.

    ``d``
        Destination node. If ``d`` is not specified, the algorithm is
        run normally (i.e., the paths from ``s`` to all reachable nodes
        are found). If ``d`` is specified, the algorithm is stopped when
        a path to ``d`` has been found.

    ``annex``
        Another graph that can be used to augment ``graph`` without
        altering it.

    ``cost_func``
        A function to apply to each edge to modify its base cost. The
        arguments it will be passed are the current node, a neighbor of
        the current node, the edge that connects the current node to
        that neighbor, and the edge that was previously traversed to
        reach the current node.

    ``heuristic_func``
        A function to apply at each iteration to guide the algorithm
        toward the destination (typically) instead of fanning out. It
        gets passed the same args as ``cost_func``.

    ``debug``
        If set, return additional info that may be useful for debugging.

    Returns
        A predecessor map with the following form::

            {v => (u, e, cost from v to u over e), ...}

        If ``debug`` is set, additional debugging info will be returned
        also. Currently, this info includes costs from ``s`` to reached
        nodes and the set of visited nodes.

    """
    counter = itertools.count()

    # Current known costs of paths from s to all nodes that have been
    # reached so far. Note that "reached" is not the same as "visited".
    costs = {s: 0}

    # Predecessor map for each node that has been reached from ``s``.
    # Keys are nodes that have been reached; values are tuples of
    # predecessor node, edge traversed to reach predecessor node, and
    # cost to traverse the edge from the predecessor node to the reached
    # node.
    predecessors = {s: (None, None, None)}

    # A priority queue of nodes with known costs from s. The nodes in
    # this queue are candidates for visitation. Nodes are added to this
    # queue when they are reached (but only if they have not already
    # been visited).
    visit_queue = [(0, next(counter), s)]

    # Nodes that have been visited. Once a node has been visited, it
    # won't be visited again. Note that in this context "visited" means
    # a node has been selected as having the lowest known cost (and it
    # must have been "reached" to be selected).
    visited = set()

    while visit_queue:
        # In the nodes remaining in the graph that have a known cost
        # from s, find the node, u, that currently has the shortest path
        # from s.
        cost_of_s_to_u, _, u = heapq.heappop(visit_queue)

        if u == d:
            break

        if u in visited:
            # This will happen when u has been reached from multiple
            # nodes before being visited (because multiple entries for
            # u will have been added to the visit queue).
            continue

        visited.add(u)

        if annex and u in annex and annex[u]:
            neighbors = annex[u]
        else:
            neighbors = graph[u] if u in graph else None

        if not neighbors:
            # u has no outgoing edges
            continue

        # The edge crossed to get to u
        prev_e = predecessors[u][1]

        # Check each of u's neighboring nodes to see if we can update
        # its cost by reaching it from u.
        for v in neighbors:
            # Don't backtrack to nodes that have already been visited.
            if v in visited:
                continue

            e = neighbors[v]

            # Get the cost of the edge running from u to v.
            cost_of_e = cost_func(u, v, e, prev_e) if cost_func else e

            # Cost of s to u plus the cost of u to v across e--this
            # is *a* cost from s to v that may or may not be less than
            # the current known cost to v.
            cost_of_s_to_u_plus_cost_of_e = cost_of_s_to_u + cost_of_e

            # When there is a heuristic function, we use a
            # "guess-timated" cost, which is the normal cost plus some
            # other heuristic cost from v to d that is calculated so as
            # to keep us moving in the right direction (generally more
            # toward the goal instead of away from it).
            if heuristic_func:
                additional_cost = heuristic_func(u, v, e, prev_e)
                cost_of_s_to_u_plus_cost_of_e += additional_cost

            if v not in costs or costs[v] > cost_of_s_to_u_plus_cost_of_e:
                # If the current known cost from s to v is greater than
                # the cost of the path that was just found (cost of s to
                # u plus cost of u to v across e), update v's cost in
                # the cost list and update v's predecessor in the
                # predecessor list (it's now u). Note that if ``v`` is
                # not present in the ``costs`` list, its current cost
                # is considered to be infinity.
                costs[v] = cost_of_s_to_u_plus_cost_of_e
                predecessors[v] = (u, e, cost_of_e)
                heapq.heappush(visit_queue, (cost_of_s_to_u_plus_cost_of_e, next(counter), v))

    if d is not None and d not in costs:
        raise NoPathError("Could not find a path from {0} to {1}".format(s, d))

    if debug:
        return predecessors, DebugInfo(costs, visited)

    return predecessors


def extract_shortest_path_from_predecessor_list(predecessors, d):
    """Extract ordered lists of nodes, edges, costs from predecessor list.

    ``predecessors``
        Predecessor list {u: (v, e), ...} u's predecessor is v via e

    ``d``
        Destination node

    Returns
        A :class:`PathInfo` object.

    """
    nodes = [d]  # Nodes on the shortest path from s to d
    edges = []  # Edges on the shortest path from s to d
    costs = []  # Costs of the edges on the shortest path from s to d
    u, e, cost = predecessors[d]
    while u is not None:
        # u is the node from which v was reached, e is the edge
        # traversed to reach v from u, and cost is the cost of u to
        # v over e. (Note that v is implicit--it's the previous u).
        nodes.append(u)
        edges.append(e)
        costs.append(cost)
        u, e, cost = predecessors[u]
    nodes.reverse()
    edges.reverse()
    costs.reverse()
    total_cost = sum(costs)
    return PathInfo(nodes, edges, costs, total_cost)


class TestPathfind:
    @property
    def graph1(self) -> Graph:
        return Graph(
            {
                1: {2: 1, 3: 2},
                2: {1: 1, 4: 2, 5: 2},
                3: {4: 2},
                4: {2: 2, 3: 2, 5: 1},
                5: {2: 2, 4: 1},
            }
        )

    @property
    def graph2(self) -> Graph:
        return Graph(
            {
                "a": {"b": 10, "d": 1},
                "b": {"a": 1, "c": 2, "e": 3},
                "c": {"b": 1, "f": 2},
                "d": {"a": 1, "e": 2, "g": 3},
                "e": {"b": 1, "d": 2, "f": 3, "h": 4},
                "f": {"c": 1, "e": 2, "i": 3},
                "g": {"d": 1, "h": 2},
                "h": {"e": 1, "g": 2, "i": 3},
                "i": {"f": 1, "h": 2},
            }
        )

    @property
    def grid(self) -> Graph:
        # 100 x 100 grid
        grid = Graph()
        grid_range_end = 101
        for i in range(1, grid_range_end):
            for j in range(1, grid_range_end):
                neighbors = {}
                if j - 1 > 0:
                    neighbors[(i, j - 1)] = 1
                if i - 1 > 0:
                    neighbors[(i - 1, j)] = 1
                if i + 1 < grid_range_end:
                    neighbors[(i + 1, j)] = 1
                if j + 1 < grid_range_end:
                    neighbors[(i, j + 1)] = 1
                grid[(i, j)] = neighbors
        return grid

    @property
    def graph3(self):
        graph = Graph(
            {
                "a": {"b": 10, "c": 100, "d": 1},
                "b": {"c": 10},
                "d": {"b": 1, "e": 1},
                "e": {"f": 1},
            }
        )

        graph.add_edge("f", "c", 1)
        graph.add_edge("g", "b", 1)

        nodes = sorted(graph)
        assert nodes == ["a", "b", "c", "d", "e", "f", "g"]

        return graph

    def test_find_path_1(self):
        result = find_path(self.graph1, 1, 4)
        nodes, edges, costs, total_cost = result
        assert nodes == [1, 2, 4]
        assert edges == [1, 2]
        assert costs == [1, 2]
        assert total_cost == 3

    def test_find_path_with_annex(self):
        annex = Graph({-1: {1: 1}, 4: {-2: 1}})
        result = find_path(self.graph1, -1, -2, annex=annex)
        nodes, edges, costs, total_cost = result
        assert nodes == [-1, 1, 2, 4, -2]
        assert edges == [1, 1, 2, 1]
        assert costs == edges
        assert total_cost == 5

    def test_path_with_cost_func(self):
        graph = {
            "a": {"b": (1, 10, "A"), "c": (1.5, 2, "C")},
            "b": {"c": (1, 2, "B"), "d": (1, 10, "A")},
            "c": {"b": (1, 3, "B"), "d": (1.5, 2, "D")},
        }

        def cost_func(u, v, e, prev_e):
            cost = e[0]
            cost *= e[1]
            if prev_e is not None and e[2] != prev_e[2]:
                cost *= 1.25
            return cost

        result = find_path(graph, "a", "d", cost_func=cost_func)
        nodes, edges, costs, total_cost = result
        assert nodes == ["a", "c", "d"]

    def test_find_path_with_heuristic(self):
        def heuristic(u, v, e, prev_e):
            # Straight line distance between current `u` and `d`
            x1, y1 = u
            x2, y2 = d
            cost = math.sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))
            return cost

        s = (41, 41)
        d = (45, 43)

        no_heuristic_predecessors, no_heuristic_info = single_source_shortest_paths(
            self.grid, s, d, debug=True
        )
        predecessors, heuristic_info = single_source_shortest_paths(
            self.grid, s, d, heuristic_func=heuristic, debug=True
        )

        # A smoke test to show the heuristic causes less fanning out
        # than when the heuristic isn't used.
        assert len(heuristic_info.visited) < len(no_heuristic_info.visited)

        result = extract_shortest_path_from_predecessor_list(predecessors, d)
        nodes, edges, costs, total_cost = result

        assert nodes[0] == s
        assert nodes[-1] == d
        assert edges == costs
        assert total_cost == 6

    def test_find_path_2(self):
        path = find_path(self.graph2, "a", "i")[0]
        assert path == ["a", "d", "e", "f", "i"]

    def test_find_path_3(self):
        path = find_path(self.graph3, "a", "c")[0]
        assert path == ["a", "d", "e", "f", "c"]

    def test_unreachable_dest(self):
        with pytest.raises(NoPathError):
            find_path(self.graph3, "c", "a")

    def test_nonexistent_dest(self):
        with pytest.raises(NoPathError):
            find_path(self.graph3, "a", "z")

    def test_all_paths(self):
        paths = single_source_shortest_paths(self.graph3, "a")
        expected = {
            "a": (None, None, None),
            "d": ("a", 1, 1),
            "b": ("d", 1, 1),
            "e": ("d", 1, 1),
            "f": ("e", 1, 1),
            "c": ("f", 1, 1),
        }
        assert paths == expected

    def test_start_and_destination_same(self):
        result = find_path(self.graph1, 1, 1)
        nodes, edges, costs, total_cost = result
        assert nodes == [1]
        assert edges == []
        assert costs == []
        assert total_cost == 0
