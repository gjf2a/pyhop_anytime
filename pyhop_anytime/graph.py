import math
import random
import heapq
from typing import TypeVar, Tuple, List, Container, Iterable

# Temporary patch until this is implemented: https://peps.python.org/pep-0673/
Self = TypeVar("Self", bound="Graph")


def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def random_coordinate(bound: float) -> float:
    return (random.random() * bound) - bound/2


class Graph:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
        self.nodes = []
        self.edges = []
        self.mst = {}
        self.mst_cost = 0.0
        self.dist = []
        self.prev = []

    def print_graph(self, node_char=lambda node: 'O'):
        for node in range(self.num_nodes()):
            print(f"{node} ({node_char(node)})", end='')
            for target, cost in self.edges[node].items():
                print(f" ({target} [{cost:.2f}])", end='')
            print()

    def num_nodes(self) -> int:
        return len(self.nodes)

    def all_nodes(self) -> List[int]:
        return [n for n in range(self.num_nodes())]

    def add_edge(self, n1: int, n2: int):
        n1_n2 = euclidean_distance(self.nodes[n1], self.nodes[n2])
        self.edges[n1][n2] = n1_n2
        self.edges[n2][n1] = n1_n2

    def add_random_nodes_edges(self, num_nodes: int, edge_prob: float):
        self.nodes = [(random_coordinate(self.width), random_coordinate(self.height)) for i in range(num_nodes)]
        self.edges = [{} for _ in range(num_nodes)]
        for n1 in range(len(self.nodes)):
            for n2 in range(n1 + 1, len(self.nodes)):
                if random.random() < edge_prob:
                    self.add_edge(n1, n2)
        for n in range(len(self.nodes)):
            if len(self.edges[n]) == 0:
                r = random.randint(0, num_nodes - 1)
                while r != n:
                    r = random.randint(0, num_nodes - 1)
                self.add_edge(n, r)

    # Adapted from: https://reintech.io/blog/pythonic-way-of-implementing-kruskals-algorithm
    # In spite of what the author above says, this is actually Prim's Algorithm.
    def minimum_spanning_tree(self):
        num_nodes = len(self.nodes)
        edges = [(cost, 0, dest) for dest, cost in self.edges[0].items()]
        heapq.heapify(edges)
        visited = {0}
        self.mst = {i: [] for i in range(num_nodes)}
        self.mst_cost = 0

        while edges:
            cost, src, dest = heapq.heappop(edges)
            if dest not in visited:
                visited.add(dest)
                self.mst[src].append(dest)
                self.mst_cost += cost
                for successor in range(num_nodes):
                    if successor not in visited:
                        heapq.heappush(edges, (euclidean_distance(self.nodes[dest], self.nodes[successor]),
                                               dest,
                                               successor))

    def mst_ready(self) -> bool:
        return self.num_nodes() == len(self.mst)

    def mst_tsp_tour(self) -> List[int]:
        if not self.mst_ready():
            self.minimum_spanning_tree()
        visited = []
        self.dfs_mst_from(0, visited)
        return visited

    def dfs_mst_from(self, node: int, visited: List[int]):
        if node not in visited:
            visited.append(node)
            for child in self.mst[node]:
                self.dfs_mst_from(child, visited)

    def tour_cost(self, tour) -> float:
        return sum(self.edges[tour[i]][tour[(i + 1) % len(tour)]] for i in range(len(tour)))

    def all_pairs_shortest_paths(self):
        # This implementation of the Floyd-Warshall algorithm is derived from Chapter 22 of:
        # https://books.goalkicker.com/AlgorithmsBook/
        self.dist = [{} for _ in range(self.num_nodes())]
        self.prev = [{} for _ in range(self.num_nodes())]
        for n1 in range(self.num_nodes()):
            self.dist[n1][n1] = 0
            self.prev[n1][n1] = n1
            for n2, cost in self.edges[n1].items():
                self.dist[n1][n2] = cost
                self.prev[n1][n2] = n1
        for k in range(self.num_nodes()):
            for i in range(self.num_nodes()):
                for j in range(self.num_nodes()):
                    i2j = self.dist[i].get(j)
                    i2k = self.dist[i].get(k)
                    k2j = self.dist[k].get(j)
                    if not (i2k is None or k2j is None) and (i2j is None or i2j > i2k + k2j):
                        self.dist[i][j] = i2k + k2j
                        self.prev[i][j] = self.prev[k][j]

    def shortest_paths_ready(self) -> bool:
        return len(self.dist) == len(self.nodes)

    def next_step_from_to(self, current: int, goal: int) -> int:
        if not self.shortest_paths_ready():
            self.all_pairs_shortest_paths()
        return self.prev[goal][current]

    def metric_closure_graph(self, nodes_of_interest: Iterable[int]) -> Self:
        if not self.shortest_paths_ready():
            self.all_pairs_shortest_paths()
        metric_closure = Graph(self.width, self.height)
        node_map = {}
        for n in nodes_of_interest:
            node_map[n] = len(metric_closure.nodes)
            metric_closure.nodes.append(self.nodes[n])
            metric_closure.edges.append({})
        for n1 in self.all_nodes():
            for n2 in self.all_nodes():
                if n1 in node_map and n2 in node_map:
                    m1 = node_map[n1]
                    m2 = node_map[n2]
                    metric_closure.edges[m1][m2] = self.dist[n1][n2]
        return metric_closure

    def approximate_steiner_cost(self, nodes_of_interest: Iterable[int]) -> float:
        mc = self.metric_closure_graph(nodes_of_interest)
        mc.minimum_spanning_tree()
        return mc.mst_cost
