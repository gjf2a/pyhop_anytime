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
from pyhop_anytime import State, TaskList, Planner, within, Facing, manhattan_distance, projection, \
    generate_grid_obstacles, a_star, show_grid
import random


def in_bounds(state, p):
    return within(p, state.width, state.height)


def project_towards(state, at, facing):
    if state.at == at and state.facing == facing:
        return projection(state.obstacles, state.width, state.height, at, facing)


def move_one_step(state, at, facing):
    future = project_towards(state, at, facing)
    if future:
        state.at = future
        state.just_turned = False
        state.visited.add((future, facing))
        return state


def turn_to(state, facing):
    state.facing = facing
    state.visited.add((state.at, facing))
    state.just_turned = True
    return state


def find_route(state, at, facing, goal):
    if at == state.at and facing == state.facing:
        if at == goal:
            return TaskList(completed=True)
        tasks = []
        future = project_towards(state, at, facing)
        if future and (future, facing) not in state.visited:
            tasks.append([('move_one_step', at, facing), ('find_route', future, facing, goal)])
        if not state.just_turned:
            for f in Facing:
                if f != facing:
                    projected = projection(state.obstacles, state.width, state.height, at, f)
                    if projected and (projected, f) not in state.visited:
                        tasks.append([('turn_to', f), ('find_route', at, f, goal)])
        # if len(tasks) == 0:
        #     projections = []
        #     for f in Facing:
        #         if f != facing:
        #             p = projection(state, at, f)
        #             if p:
        #                 projections.append((p, (p, f) in state.visited))
        #     print(f"at: {at} facing: {facing} future: {future} ({(future, facing) in state.visited}) turned: {state.just_turned} projections: {projections}")
        return TaskList(tasks)


def generate_grid_world(width, height, start, start_facing, capacity, num_packages, num_obstacles):
    state = State(f"grid_{width}x{height}_at_{start}_{capacity}_capacity_{num_packages}_packages_{num_obstacles}_obstacles")
    state.at = start
    state.holding = [None] * capacity
    state.facing = start_facing
    state.width = width
    state.height = height
    state.obstacles = generate_grid_obstacles(width, height, num_obstacles)

    package_candidates = [(x, y) for x in range(width - 1) for y in range(height - 1)]
    random.shuffle(package_candidates)
    state.package_locations = package_candidates[:num_packages]
    package_goal_candidates = [(x, y) for x in range(width - 1) for y in range(height - 1)]
    state.package_goals = package_goal_candidates[:num_packages]
    return state, [('find_route', start, start_facing, end)]


def make_grid_planner():
    p = Planner()
    p.declare_operators(move_one_step, turn_to)
    p.declare_methods(find_route)
    return p


if __name__ == '__main__':
    max_seconds = 4
    state, tasks = generate_grid_world(7, 7, (1, 0), Facing.NORTH, (2, 6), 10, 30)
    optimal = a_star(state.obstacles, state.width, state.height, (1, 0), (2, 6))
    show_grid(state.obstacles, state.width, state.height)
    print(optimal)
    if optimal:
        planner = make_grid_planner()
        print("Anyhop")
        plan_times = planner.anyhop(state, tasks, max_seconds=max_seconds)
        print(f"{len(plan_times)} plans")
        if len(plan_times) > 0:
            print(plan_times[-1][1], plan_times[-1][2])
        print()
        print("Action Tracker")
        plan_times = planner.anyhop_random_tracked(state, tasks, max_seconds=max_seconds)
        print(f"{len(plan_times)} plans")
        if len(plan_times) > 0:
            print(plan_times[-1][1], plan_times[-1][2])
        print()
