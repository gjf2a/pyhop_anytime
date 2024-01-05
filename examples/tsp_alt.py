# Alternative implementation of TSP, experimenting with using the MST to influence the probabilities of
# selecting particular actions.
#
# This is a fairly interesting solution.
# I need to do some more work to evaluate it. Preliminary results are mixed.

from pyhop_anytime import State, TaskList, Planner
from tsp import euclidean_distance, random_coordinate, spanning_tree, move, summarize


def make_metric_tsp_state(num_cities, width, height):
    state = State(f"tsp_{num_cities}_cities_{width}x{height}")
    state.locations = [(random_coordinate(width), random_coordinate(height)) for i in range(num_cities)]
    state.at = 0
    state.visited = {}
    state.mst = spanning_tree(state)[0]
    return state, [('nondeterministic_choice',)]


def nondeterministic_choice(state):
    if len(state.visited) == len(state.locations):
        return TaskList(completed=True)
    tasks = []
    for city in range(1, len(state.locations)):
        if city not in state.visited:
            task = [('move', city), ('nondeterministic_choice',)]
            tasks.append(task)
            if state.mst.get(city) == state.at or state.mst.get(state.at) == city:
                tasks.append(task)
    if len(tasks) == 0:
        return TaskList([('move', 0)])
    else:
        return TaskList(tasks)


def tsp_planner():
    planner = Planner(cost_func=lambda state, step: euclidean_distance(state.locations[state.at],
                                                                       state.locations[step[1]]))
    planner.declare_operators(move)
    planner.declare_methods(nondeterministic_choice)
    return planner


if __name__ == '__main__':
    p = tsp_planner()
    s, t = make_metric_tsp_state(25, 200, 200)
    mst_size = spanning_tree(s)[1]
    print(f"Minimum spanning tree: {mst_size:7.2f}")
    max_seconds = 5
    summarize("Random no-max", mst_size, p.anyhop_random(s, t, use_max_cost=False, max_seconds=max_seconds))
    summarize("Random incremental", mst_size, p.anyhop_random_incremental(s, t, max_seconds=max_seconds))


