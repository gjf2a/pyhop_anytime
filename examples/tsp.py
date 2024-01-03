from pyhop_anytime import State, TaskList, Planner
import random
import math


def euclidean_distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def random_coordinate(bound):
    return (random.random() * bound) - bound/2


def make_metric_tsp_state(num_cities, width, height):
    state = State(f"tsp_{num_cities}_cities_{width}x{height}")
    state.locations = [(random_coordinate(width), random_coordinate(height)) for i in range(num_cities)]
    state.distances = [[euclidean_distance(state.locations[i], state.locations[j]) for j in range(num_cities)] for i in range(num_cities)]
    state.at = 0
    state.visited = {}
    state.tour_cost = 0
    return state, [('nondeterministic_choice',)]


def move(state, new_city):
    if new_city not in state.visited:
        state.tour_cost += state.distances[state.at][new_city]
        state.visited[new_city] = state.distances[state.at][new_city]
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
    planner = Planner(cost_func=lambda state, step: state.distances[state.at][step[1]])
    planner.declare_operators(move)
    planner.declare_methods(nondeterministic_choice)
    return planner


if __name__ == '__main__':
    p = tsp_planner()
    s, t = make_metric_tsp_state(10, 200, 200)
    print(p.anyhop(s, t, max_seconds=3))
    print(p.anyhop_random(s, t, max_seconds=3))
