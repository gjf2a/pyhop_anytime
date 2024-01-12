# Rewrite this as follows:
#
# * The delivery robot has a capacity of a certain number of packages it can carry.
# * The map is seeded with a potentially differing number of packages, each of which has a destination.
# * Before planning begins, we compute all-pairs-shortest-paths.
# * We nondeterministically select packages to deliver equal to the capacity.
#   * We follow a path to the packages as long as they agree.
#   * When the paths diverge, we nondeterministically select which way to go. We then "commit" to the packages that
#     share that path until they are retrieved.
#   * When a package is retrieved, we nondeterministically select among the delivery destinations and additional
#     packages.
#
# The purpose of this example:
# * Trying to use pyhop to solve simple grid problems with depth-first search is not my concept of its use. It isn't
#   the right tool for that job, because A* will reliably find the optimal solution in polynomial time.
# * pyhop is the right tool for a job where the problem is NP-Complete. We can generate a valid solution in
#   polynomial time but an optimal solution is hard to find. We bring to bear all polynomial-time resources to solve
#   it, including auxiliary searches specialized to a task.
from pyhop_anytime import State, TaskList, Planner, Facing, Grid, facing_from_to
import random


def deliver_all(state):
    deliveries = []
    for package, start in enumerate(state.package_locations):
        if state.package_goals[package] != start:
            deliveries.append([('retrieve_package', package), ('deliver_holding',), ('deliver_all',)])
    if len(deliveries) == 0:
        return TaskList(completed=True)
    else:
        return TaskList(deliveries)


def retrieve_package(state, package):
    base_option = [('go_to', state.at, state.package_locations[package]), ('pick_up', package)]
    options = [base_option]
    if len(state.holding) + 1 < state.capacity:
        for alt_package, alt_start in enumerate(state.package_locations):
            if package != alt_package and state.package_goals[alt_package] != alt_start:
                options.append(base_option + [('retrieve_package', alt_package)])
    return TaskList(options)


def deliver_holding(state):
    if len(state.holding) == 1:
        return TaskList([('go_to', state.at, state.package_goals[state.holding[0]]), ('put_down', state.holding[0])])
    else:
        options = []
        for package in state.holding:
            options.append([('go_to', state.at, state.package_goals[package]), ('put_down', package), ('deliver_holding',)])
        return TaskList(options)


def pick_up(state, package):
    if state.at == state.package_locations[package] and len(state.holding) < state.capacity:
        state.package_locations[package] = 'robot'
        state.holding.append(package)
        return state


def put_down(state, package):
    if package in state.holding:
        state.package_locations[package] = state.at
        state.holding.remove(package)
        return state


def go_to(state, start, end):
    if state.at == start:
        path = state.grid.shortest_path_between(start, end)
        actions = []
        prev_facing = state.facing
        for i, current in enumerate(path):
            if i > 0:
                prev = path[i - 1]
                f = facing_from_to(prev, current)
                if f is None:
                    return None
                if f != prev_facing:
                    actions.append(('turn_to', f))
                actions.append(('move_one_step', prev, f))
                prev_facing = f
        return TaskList(actions)

########

def in_bounds(state, p):
    return state.grid.within(p)


def project_towards(state, at, facing):
    if state.at == at and state.facing == facing:
        return state.grid.projection(at, facing)


def move_one_step(state, at, facing):
    future = project_towards(state, at, facing)
    if future:
        state.at = future
        state.just_turned = False
        return state


def turn_to(state, facing):
    state.facing = facing
    state.just_turned = True
    return state


def generate_grid_world(width, height, start, start_facing, capacity, num_packages, num_obstacles):
    state = State(f"grid_{width}x{height}_{start}_to_{num_obstacles}_obstacles_{num_packages}_packages_{capacity}_capacity")
    state.at = start
    state.facing = start_facing
    state.width = width
    state.height = height
    state.just_turned = False
    state.grid = Grid(width, height)
    state.grid.add_random_obstacles(num_obstacles)
    state.capacity = capacity
    state.holding = []

    package_candidates = state.grid.all_locations()
    random.shuffle(package_candidates)
    state.package_locations = package_candidates[:num_packages]
    package_goal_candidates = state.grid.all_locations()
    for start in state.package_locations:
        package_goal_candidates.remove(start)
    random.shuffle(package_goal_candidates)
    state.package_goals = package_goal_candidates[:num_packages]
    return state, [('deliver_all',)]


def make_grid_planner():
    p = Planner()
    p.declare_operators(move_one_step, turn_to, pick_up, put_down)
    p.declare_methods(deliver_all, retrieve_package, deliver_holding, go_to)
    return p


if __name__ == '__main__':
    max_seconds = 4
    state, tasks = generate_grid_world(5, 5, (2, 2), Facing.NORTH, 2, 3, 30)
    state.grid.print_grid(lambda location: 'P' if location in state.package_locations else 'R' if location == state.at else 'G' if location in state.package_goals else 'O')
    planner = make_grid_planner()
    print("Anyhop")
    plan_times = planner.anyhop(state, tasks, max_seconds=max_seconds)
    print(f"{len(plan_times)} plans")
    if len(plan_times) > 0:
        print(plan_times[-1][1], plan_times[-1][2])
        print(plan_times[-1][0])
    print()
    print("Action Tracker")
    plan_times = planner.anyhop_random_tracked(state, tasks, max_seconds=max_seconds)
    print(f"{len(plan_times)} plans")
    if len(plan_times) > 0:
        print(plan_times[-1][1], plan_times[-1][2])
        print(plan_times[-1][0])
    print()
