## The purpose of this example:
# * Trying to use pyhop to solve simple grid problems with depth-first search is not my concept of its use. It isn't
#   the right tool for that job, because A* will reliably find the optimal solution in polynomial time.
# * pyhop is the right tool for a job where the problem is NP-Complete. We can generate a valid solution in
#   polynomial time but an optimal solution is hard to find. We bring to bear all polynomial-time resources to solve
#   it, including auxiliary searches specialized to a task.

from pyhop_anytime import State, TaskList, Planner, Graph
from pyhop_anytime.stats import experiment
import random


def deliver_all_packages_from(state, current):
    possibilities = []
    for package, goal in enumerate(state.package_goals):
        if state.package_locations[package] != goal:
            if state.package_locations[package] == 'robot':
                possibilities.append((package, goal))
            elif len(state.holding) < state.capacity:
                possibilities.append((package, state.package_locations[package]))
    if len(possibilities) == 0:
        return TaskList(completed=True)
    else:
        possibilities.sort()
        return TaskList([('possible_destinations', current, tuple(possibilities))])


def possible_destinations(state, current, possibilities):
    for (package, goal) in possibilities:
        if current == goal:
            if state.package_locations[package] == current:
                return TaskList([('pick_up', package), ('deliver_all_packages_from', current)])
            elif state.package_goals[package] == current:
                return TaskList([('put_down', package), ('deliver_all_packages_from', current)])
            else:
                assert False

    assert len(possibilities) > 0
    if len(possibilities) == 1:
        package, goal = possibilities[0]
        return TaskList([('progress_task_list', current, state.graph.next_step_from_to(current, goal), possibilities)])
    else:
        options = {}
        for (package, goal) in possibilities:
            option = state.graph.next_step_from_to(current, goal)
            if option not in options:
                options[option] = []
            options[option].append((package, goal))
        tasks = [[('progress_task_list', current, new_current, tuple(sorted(new_possible)))]
                 for new_current, new_possible in options.items()]
        return TaskList(tasks)


def progress_task_list(state, current, new_current, new_possible):
    assert state.at == current
    return TaskList([('move_one_step', current, new_current), ('possible_destinations', new_current, new_possible)])


def move_one_step(state, start, end):
    assert state.at == start
    state.at = end
    return state


def pick_up(state, package):
    assert state.at == state.package_locations[package] and len(state.holding) < state.capacity
    state.package_locations[package] = 'robot'
    state.holding.append(package)
    return state


def put_down(state, package):
    assert package in state.holding
    state.package_locations[package] = state.at
    state.holding.remove(package)
    return state


def generate_graph_world(width, height, capacity, num_locations, edge_prob, num_packages):
    state = State(f"graph_{width}x{height}_{num_packages}_packages_{capacity}_capacity")
    state.at = 0
    state.width = width
    state.height = height
    state.graph = Graph(width, height)
    state.graph.add_random_nodes_edges(num_locations, edge_prob)
    state.capacity = capacity
    state.holding = []

    package_candidates = state.graph.all_nodes()
    random.shuffle(package_candidates)
    state.package_locations = package_candidates[:num_packages]
    package_goal_candidates = state.graph.all_nodes()
    for start in state.package_locations:
        package_goal_candidates.remove(start)
    random.shuffle(package_goal_candidates)
    state.package_goals = package_goal_candidates[:num_packages]
    return state, [('deliver_all_packages_from', state.at)]


def copy_graph_state(state):
    new_state = State(state.__name__)

    # Unchanging elements
    new_state.width = state.width
    new_state.height = state.height
    new_state.graph = state.graph
    new_state.capacity = state.capacity
    new_state.package_goals = state.package_goals

    # Changing scalar elements
    new_state.at = state.at

    # Changing collection elements
    new_state.holding = state.holding[:]
    new_state.package_locations = state.package_locations[:]

    return new_state


def action_cost(state, step):
    if step[0] == 'move_one_step':
        return state.graph.edges[step[1]][step[2]]
    else:
        return 1.0


def make_graph_planner():
    p = Planner(copy_func=copy_graph_state, cost_func=action_cost)
    p.declare_operators(move_one_step, pick_up, put_down)
    p.declare_methods(deliver_all_packages_from, possible_destinations, progress_task_list)
    return p


if __name__ == '__main__':
    planner = make_graph_planner()
    experiment(num_problems=2,
               runs_per_problem=3,
               max_seconds=2,
               problem_generator=lambda: generate_graph_world(100, 100, capacity=3, num_locations=36, edge_prob=0.25,
                                                              num_packages=12),
               non_random_planners={"DFS": lambda state, tasks, max_seconds: planner.anyhop(state, tasks,
                                                                                            max_seconds=max_seconds)},
               random_planners={
                   "Random": lambda state, tasks, max_seconds: planner.anyhop_random(state, tasks, use_max_cost=False,
                                                                                     max_seconds=max_seconds),
                   "Tracker1": lambda state, tasks, max_seconds: planner.anyhop_random_tracked(state, tasks,
                                                                                               ignore_single=True,
                                                                                               max_seconds=max_seconds),
                   "Tracker2": lambda state, tasks, max_seconds: planner.anyhop_random_tracked(state, tasks,
                                                                                               ignore_single=False,
                                                                                               max_seconds=max_seconds)
               }
               )
