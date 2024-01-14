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
        return TaskList([('possible_destinations', current, possibilities)])


def possible_destinations(state, current, possibilities):
    for (package, goal) in possibilities:
        if current == goal:
            if state.package_locations[package] == current:
                return TaskList([('pick_up', package), ('deliver_all_packages_from', current)])
            elif state.package_goals[package] == current:
                return TaskList([('put_down', package), ('deliver_all_packages_from', current)])
            else:
                assert False

    if len(possibilities) == 0:
        assert False
    elif len(possibilities) == 1:
        package, goal = possibilities[0]
        task_list = progress_task_list(state, current, state.grid.next_step_from_to(current, goal), possibilities)
        return TaskList(task_list)
    else:
        options = {}
        for (package, goal) in possibilities:
            option = state.grid.next_step_from_to(current, goal)
            if option not in options:
                options[option] = []
            options[option].append((package, goal))
        tasks = [progress_task_list(state, current, new_current, sorted(new_possible))
                 for new_current, new_possible in options.items()]
        return TaskList(tasks)


def progress_task_list(state, current, new_current, new_possible):
    task_list = []
    target_facing = facing_from_to(current, new_current)
    if state.facing != target_facing:
        task_list.append(('turn_to', target_facing))
    task_list.append(('move_one_step', current, target_facing))
    task_list.append(('possible_destinations', new_current, new_possible))
    return task_list

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
        return state
    else:
        assert False


def turn_to(state, facing):
    state.facing = facing
    return state


def pick_up(state, package):
    if state.at == state.package_locations[package] and len(state.holding) < state.capacity:
        state.package_locations[package] = 'robot'
        state.holding.append(package)
        return state
    else:
        assert False


def put_down(state, package):
    if package in state.holding:
        state.package_locations[package] = state.at
        state.holding.remove(package)
        return state
    else:
        assert False


def generate_grid_world(width, height, start, start_facing, capacity, num_packages, num_obstacles):
    state = State(f"grid_{width}x{height}_{start}_to_{num_obstacles}_obstacles_{num_packages}_packages_{capacity}_capacity")
    state.at = start
    state.facing = start_facing
    state.width = width
    state.height = height
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
    return state, [('deliver_all_packages_from', state.at)]


def copy_grid_state(state):
    new_state = State(state.__name__)

    # Unchanging elements
    new_state.width = state.width
    new_state.height = state.height
    new_state.grid = state.grid
    new_state.capacity = state.capacity
    new_state.package_goals = state.package_goals

    # Changing scalar elements
    new_state.at = state.at
    new_state.facing = state.facing

    # Changing collection elements
    new_state.holding = state.holding[:]
    new_state.package_locations = state.package_locations[:]

    return new_state


def make_grid_planner():
    p = Planner(copy_func=copy_grid_state)
    p.declare_operators(move_one_step, turn_to, pick_up, put_down)
    p.declare_methods(deliver_all_packages_from, possible_destinations)
    return p


if __name__ == '__main__':
    max_seconds = 10
    state, tasks = generate_grid_world(5, 5, (2, 2), Facing.NORTH, 3, 6, 10)
    state.grid.print_grid(lambda location: 'P' if location in state.package_locations else 'R' if location == state.at else 'G' if location in state.package_goals else 'O')
    planner = make_grid_planner()
    print("Anyhop")
    plan_times = planner.anyhop(state, tasks, max_seconds=max_seconds)
    print(f"{len(plan_times)} plans")
    if len(plan_times) > 0:
        #for step in plan_times[-1][0]:
        #    print(step)
        print(plan_times[-1][1], plan_times[-1][2])
    print()
    print("Action Tracker")
    plan_times = planner.anyhop_random_tracked(state, tasks, max_seconds=max_seconds)
    print(f"{len(plan_times)} plans")
    if len(plan_times) > 0:
        #for step in plan_times[-1][0]:
        #    print(step)
        print(plan_times[-1][1], plan_times[-1][2])
    print()
