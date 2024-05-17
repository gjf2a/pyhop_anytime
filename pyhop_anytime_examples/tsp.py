import os
import random

from pyhop_anytime import State, TaskList, Planner
from pyhop_anytime.graph import Graph
from pyhop_anytime.stats import experiment


def make_metric_tsp_state(num_cities, width, height):
    state = State(f"tsp_{num_cities}_cities_{width}x{height}")
    state.graph = Graph()
    state.graph.add_random_nodes_edges(num_cities, 1.0, width, height)
    state.at = 0
    return tsp_kickoff(state)


def tsp_kickoff(state):
    state.visited = set()
    return state, [('complete_tour_from', state.at)]


def move(state, current_city, new_city):
    if state.at == current_city and new_city not in state.visited:
        state.visited.add(new_city)
        state.at = new_city
        return state


def complete_tour_from(state, current_city):
    if len(state.visited) == state.graph.num_nodes():
        return TaskList(completed=True)

    tasks = [[('move', current_city, city), ('complete_tour_from', city)]
             for city in state.graph.all_nodes() if city not in state.visited and city != current_city]
    assert len(tasks) > 0
    return TaskList(tasks)


def tsp_planner():
    planner = Planner(cost_func=lambda state, step: state.graph.edges[state.at][step[2]])
    planner.declare_operators(move)
    planner.declare_methods(complete_tour_from)
    return planner


def summarize(header, mst_size, mst_tour_size, plans):
    print(f"{header}: {len(plans)} plans")
    print(
        f"First cost {plans[0][1]:7.2f}\tMST Ratio: {plans[0][1] / mst_size:7.2f}\tMST Tour Ratio: {plans[0][1] / mst_tour_size:7.2f}\ttime {plans[0][2]:4.2f}")
    print(
        f"Last cost  {plans[-1][1]:7.2f}\tMST Ratio: {plans[-1][1] / mst_size:7.2f}\tMST Tour Ratio: {plans[-1][1] / mst_tour_size:7.2f}\ttime {plans[-1][2]:4.2f}")


def make_state_report_mst(num_cities):
    state, tasks = make_metric_tsp_state(num_cities, 200, 200)
    tour = state.graph.mst_tsp_tour()
    visited_cost = state.graph.tour_cost(tour)
    print(f"Minimum spanning tree: {state.graph.mst_cost:7.2f}")
    print(f"MST tour cost: {visited_cost:7.2f}\tMST Ratio: {visited_cost / state.graph.mst_cost:7.2f}")
    return state, tasks


def tsp2graph(filename: str, shuffle_city_order: bool) -> Graph:
    with open(filename) as fin:
        started = False
        node_lines = []
        for line in fin:
            if line.strip() == "EOF":
                started = False
            if started:
                node_lines.append(line)
            if line.strip() == "NODE_COORD_SECTION":
                started = True

        result = Graph()
        if shuffle_city_order:
            random.shuffle(node_lines)
        for line in node_lines:
            name, x, y = line.split()
            result.add_node(int(name), (float(x), float(y)))
        result.add_all_possible_edges()
        return result


def tsp2planning(filename: str, shuffle_city_order=False):
    state = State(f"{filename}")
    state.graph = tsp2graph(filename, shuffle_city_order)
    city = random.randint(0, state.graph.num_nodes() - 1) if shuffle_city_order else 0
    state.at = state.graph.all_nodes()[city]
    return tsp_kickoff(state)


def tsp_experiment(num_cities, max_seconds):
    print(f"{num_cities} cities, {max_seconds}s time limit")
    p = tsp_planner()
    experiment(num_problems=2,
               runs_per_problem=3,
               max_seconds=max_seconds,
               problem_generator=lambda: make_state_report_mst(num_cities),
               non_random_planners={"DFS": lambda state, tasks, max_seconds: p.anyhop(state, tasks,
                                                                                      max_seconds=max_seconds)},
               random_planners={
                   "Random": lambda state, tasks, max_seconds: p.anyhop_random(state, tasks, use_max_cost=False,
                                                                               max_seconds=max_seconds),
                   "Tracker1": lambda state, tasks, max_seconds: p.anyhop_random_tracked(state, tasks,
                                                                                         ignore_single=True,
                                                                                         max_seconds=max_seconds),
                   "Tracker2": lambda state, tasks, max_seconds: p.anyhop_random_tracked(state, tasks,
                                                                                         ignore_single=False,
                                                                                         max_seconds=max_seconds)
               }
               )


if __name__ == '__main__':
    print("att48.tsp experiment")
    p = tsp_planner()
    experiment(num_problems=2, runs_per_problem=2, max_seconds=3,
               problem_generator=lambda: tsp2planning("att48.tsp", True),
               non_random_planners={"DFS": lambda state, tasks, max_seconds: p.anyhop(state, tasks,
                                                                                      max_seconds=3)},
               random_planners={
                   "Random": lambda state, tasks, max_seconds: p.anyhop_random(state, tasks, use_max_cost=False,
                                                                               max_seconds=3),
                   "Tracker1": lambda state, tasks, max_seconds: p.anyhop_random_tracked(state, tasks,
                                                                                         ignore_single=True,
                                                                                         max_seconds=3),
                   "Tracker2": lambda state, tasks, max_seconds: p.anyhop_random_tracked(state, tasks,
                                                                                         ignore_single=False,
                                                                                         max_seconds=3)
               })
    print()
    print()
    print("berlin52.tsp experiment")
    experiment(num_problems=1, runs_per_problem=2, max_seconds=3,
               problem_generator=lambda: tsp2planning("berlin52.tsp", False),
               non_random_planners={"DFS": lambda state, tasks, max_seconds: p.anyhop(state, tasks,
                                                                                      max_seconds=3)},
               random_planners={
                   "Random": lambda state, tasks, max_seconds: p.anyhop_random(state, tasks, use_max_cost=False,
                                                                               max_seconds=3),
                   "Tracker1": lambda state, tasks, max_seconds: p.anyhop_random_tracked(state, tasks,
                                                                                         ignore_single=True,
                                                                                         max_seconds=3),
                   "Tracker2": lambda state, tasks, max_seconds: p.anyhop_random_tracked(state, tasks,
                                                                                         ignore_single=False,
                                                                                         max_seconds=3),
                   "Tracker3": lambda state, tasks, max_seconds: p.anyhop_random_tracked_dfs_seed(state, tasks,
                                                                                         max_seconds=3)
               })
    print()
    print()
    tsp_experiment(25, 5)
    print()
    print()
    tsp_experiment(50, 30)
    print()
    print()
