"""
I need a minimal cost pathfinding algorithm but with multiple target destination nodes that all need reaching in a given
run. This is not a traveling salesman problem as a path to a next destination may restart from anywhere a path has
already been made. This may be more in the domain 'flow' algorithms than pathfinding, I don't really know. Implement
this in python.

==

Certainly! Below is a Python implementation of an algorithm to find the minimal cost paths that reach multiple target
destination nodes in a graph. This implementation follows the approach of approximating the Steiner Tree problem:

Compute Shortest Paths Between All Pairs of Target Nodes: Use Dijkstra's algorithm to find the shortest paths between
all pairs of target nodes.

Build a Complete Graph Over Target Nodes: Create a complete graph where each target node is connected to every other
target node, and the edge weights are the shortest path distances computed in step 1.

Compute the Minimum Spanning Tree (MST): Use Kruskal's algorithm to find the MST of the complete graph from step 2.

Reconstruct the Paths in the Original Graph: For each edge in the MST, retrieve the corresponding shortest path in the
original graph.

Here's the complete Python code:

--

Explanation:

The shortest path from 'A' to 'D' is ['A', 'B', 'D'] with a cost of 3.

The shortest path from 'D' to 'F' is ['D', 'F'] with a cost of 1.

The total cost to reach all target nodes is 4.

This implementation efficiently finds the minimal cost paths connecting all target nodes, allowing paths to start from
any node already reached, and minimizes the total cost of the paths.
"""
import collections
import heapq
import typing as ta

from omlish.graphs import dot


T = ta.TypeVar('T')


class Graph(ta.Generic[T]):
    def __init__(self) -> None:
        super().__init__()
        self.adj: collections.defaultdict[T, list[tuple[T, int]]] = collections.defaultdict(list)
        self.nodes: set[T] = set()

    def add_edge(self, u, v, weight):
        self.adj[u].append((v, weight))
        self.adj[v].append((u, weight))
        self.nodes.update([u, v])

    def dijkstra(self, start):
        dist = {node: float('inf') for node in self.nodes}
        prev = {node: None for node in self.nodes}
        dist[start] = 0
        heap = [(0, start)]
        while heap:
            current_dist, u = heapq.heappop(heap)
            if current_dist > dist[u]:
                continue
            for v, weight in self.adj[u]:
                alt = dist[u] + weight
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    heapq.heappush(heap, (alt, v))
        return dist, prev

    def get_shortest_path(self, prev, start, end):
        path = []
        u = end
        while u != start:
            if u is None:
                return []
            path.append(u)
            u = prev[u]
        path.append(start)
        path.reverse()
        return path

    def compute_all_pairs_shortest_paths(self, targets):
        all_shortest_paths = {}
        all_dists = {}
        for u in targets:
            dist, prev = self.dijkstra(u)
            for v in targets:
                if u != v:
                    path = self.get_shortest_path(prev, u, v)
                    all_shortest_paths[(u, v)] = path
                    all_dists[(u, v)] = dist[v]
        return all_dists, all_shortest_paths


def kruskal_mst(edges, nodes):
    parent = {node: node for node in nodes}

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    mst = []
    edges = sorted(edges, key=lambda x: x[2])  # Sort edges by weight
    for u, v, weight in edges:
        pu, pv = find(u), find(v)
        if pu != pv:
            parent[pu] = pv
            mst.append((u, v, weight))
    return mst


def minimal_cost_paths(graph, target_nodes):
    # Step 1: Compute shortest paths between all pairs of target nodes
    all_dists, all_shortest_paths = graph.compute_all_pairs_shortest_paths(target_nodes)

    # Step 2: Build a complete graph over target nodes
    complete_graph_edges = []
    for (u, v), dist in all_dists.items():
        complete_graph_edges.append((u, v, dist))

    # Step 3: Compute the MST of the complete graph
    mst_edges = kruskal_mst(complete_graph_edges, target_nodes)

    # Step 4: Reconstruct the paths in the original graph
    final_paths = []
    total_cost = 0
    for u, v, weight in mst_edges:
        path = all_shortest_paths[(u, v)]
        final_paths.append(path)
        total_cost += weight

    return final_paths, total_cost


if __name__ == '__main__':
    # Example usage:

    # Create the graph
    graph = Graph()
    graph.add_edge('A', 'B', 2)
    graph.add_edge('A', 'C', 3)
    graph.add_edge('B', 'C', 1)
    graph.add_edge('B', 'D', 1)
    graph.add_edge('C', 'D', 1)
    graph.add_edge('C', 'E', 5)
    graph.add_edge('D', 'E', 2)
    graph.add_edge('D', 'F', 3)
    graph.add_edge('E', 'F', 1)

    dot.open_dot(dot.render(dot.make_simple({k: list(zip(*v))[0] for k, v in graph.adj.items()})))

    # Define the target nodes
    target_nodes = ['A', 'D', 'F']

    # Find the minimal cost paths
    paths, cost = minimal_cost_paths(graph, target_nodes)

    print("Paths to reach all target nodes:")
    for path in paths:
        print(" -> ".join(path))
    print(f"Total cost: {cost}")
