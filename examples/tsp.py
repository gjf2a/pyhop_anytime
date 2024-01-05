from pyhop_anytime import State, TaskList, Planner, MonteCarloPlannerHeap
import random
import math
import heapq


def euclidean_distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def random_coordinate(bound):
    return (random.random() * bound) - bound/2


def make_metric_tsp_state(num_cities, width, height):
    state = State(f"tsp_{num_cities}_cities_{width}x{height}")
    state.locations = [(random_coordinate(width), random_coordinate(height)) for i in range(num_cities)]
    state.at = 0
    state.visited = {}
    return state, [('nondeterministic_choice',)]


# Adapted from: https://reintech.io/blog/pythonic-way-of-implementing-kruskals-algorithm
def spanning_tree(tsp_state):
    num_cities = len(tsp_state.locations)
    edges = [(euclidean_distance(tsp_state.locations[0], tsp_state.locations[i]), 0, i)
             for i in range(1, num_cities)]
    heapq.heapify(edges)
    visited = {0}
    mst = {}
    mst_cost = 0

    while edges:
        cost, src, dest = heapq.heappop(edges)
        if dest not in visited:
            visited.add(dest)
            mst[src] = dest
            mst_cost += cost
            for successor in range(num_cities):
                if successor not in visited:
                    heapq.heappush(edges, (euclidean_distance(tsp_state.locations[dest],
                                                              tsp_state.locations[successor]),
                                           dest,
                                           successor))
    return mst, mst_cost


def move(state, new_city):
    if new_city not in state.visited:
        state.visited[new_city] = True
        state.at = new_city
        return state


def nondeterministic_choice(state):
    if len(state.visited) == len(state.locations):
        return TaskList(completed=True)
    tasks = [[('move', city), ('nondeterministic_choice',)]
             for city in range(1, len(state.locations)) if city not in state.visited]
    if len(tasks) == 0:
        return TaskList([('move', 0)])
    else:
        return TaskList(tasks)


def tsp_planner():
    planner = Planner(cost_func=lambda state, step: euclidean_distance(state.locations[state.at], state.locations[step[1]]))
    planner.declare_operators(move)
    planner.declare_methods(nondeterministic_choice)
    return planner


def summarize(header, plans):
    print(f"{header}: {len(plans)} plans")
    print(f"First cost {plans[0][1]:7.2f}\ttime {plans[0][2]:4.2f}")
    print(f"Last cost  {plans[-1][1]:7.2f}\ttime {plans[-1][2]:4.2f}")


if __name__ == '__main__':
    p = tsp_planner()
    s, t = make_metric_tsp_state(25, 200, 200)
    print(f"Minimum spanning tree: {spanning_tree(s)[1]}")
    max_seconds = 5
    summarize("DFS", p.anyhop(s, t, max_seconds=max_seconds))
    summarize("Random", p.anyhop_random(s, t, max_seconds=max_seconds))
    summarize("Random no-max", p.anyhop_random(s, t, use_max_cost=False, max_seconds=max_seconds))
    summarize("Random incremental", p.anyhop_random_incremental(s, t, max_seconds=max_seconds))
    #summarize("MC", p.anyhop(s, t, max_seconds=3, queue_init=lambda: MonteCarloPlannerHeap(p, go_deep_first=False)))
    #summarize("MC go deep", p.anyhop(s, t, max_seconds=3, queue_init=lambda: MonteCarloPlannerHeap(p, go_deep_first=True)))


