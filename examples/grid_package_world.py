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

import random
import heapq
from enum import Enum

from pyhop_anytime import State, TaskList, Planner


class Facing(Enum):
    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)

    def __neg__(self):
        if self == Facing.NORTH:
            return Facing.SOUTH
        elif self == Facing.SOUTH:
            return Facing.NORTH
        elif self == Facing.EAST:
            return Facing.WEST
        else:
            return Facing.EAST

    def __add__(self, other):
        if type(other) == Facing:
            return self.value[0] + other.value[0], self.value[1] + other.value[1]
        else:
            return self.value[0] + other[0], self.value[1] + other[1]


def manhattan_distance(p1, p2):
    return sum(abs(p1[i] - p2[i]) for i in range(len(p1)))


def manhattan_neighbors(p):
    return [(p[0] + f.value[0], p[1] + f.value[1]) for f in Facing]


def in_bounds(state, p):
    return within(p, state.width, state.height)


def within(p, width, height):
    return 0 <= p[0] < width and 0 <= p[1] < height


def project_towards(state, at, facing):
    if state.at == at and state.facing == facing:
        return projection(state, at, facing)


def projection(state, at, facing):
    if (at, facing) not in state.obstacles:
        future = facing + at
        if in_bounds(state, future):
            return future


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
                    projected = projection(state, at, f)
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
    state.obstacles = set()
    obstacle_facings = [Facing.SOUTH, Facing.EAST]
    obstacle_candidates = [(x, y, f) for x in range(width - 1) for y in range(height - 1) for f in obstacle_facings]
    random.shuffle(obstacle_candidates)
    obstacle_candidate = 0
    while len(state.obstacles) < num_obstacles and obstacle_candidate < len(obstacle_candidates):
        x1, y1, f = obstacle_candidates[obstacle_candidate]
        state.obstacles.add(((x1, y1), f))
        x2, y2 = f + (x1, y1)
        state.obstacles.add(((x2, y2), -f))
        obstacle_candidate += 1
        if not all_cells_reachable(state.obstacles, state.width, state.height):
            state.obstacles.remove(((x1, y1), f))
            state.obstacles.remove(((x2, y2), -f))

    package_candidates = [(x, y) for x in range(width - 1) for y in range(height - 1)]
    random.shuffle(package_candidates)
    state.package_locations = package_candidates[:num_packages]
    package_goal_candidates = [(x, y) for x in range(width - 1) for y in range(height - 1)]
    state.package_goals = package_goal_candidates[:num_packages]
    return state, [('find_route', start, start_facing, end)]


def all_cells_reachable(obstacles, width, height):
    reached = set()
    heap = [(0, (0, 0))]
    while len(heap) > 0:
        cost, current = heapq.heappop(heap)
        if current not in reached:
            reached.add(current)
            for f in Facing:
                neighbor = f + current
                if within(neighbor, width, height) and (neighbor, f) not in obstacles:
                    heapq.heappush(heap, (1 + cost, neighbor))
    return len(reached) == width * height


def show_grid(state):
    print(" ", end='')
    for x in range(state.width):
        print(f" {x}", end='')
    print()
    for y in range(state.height):
        if y > 0:
            print("  ", end='')
            for x in range(state.width):
                if ((x, y), Facing.NORTH) in state.obstacles:
                    print("_ ", end='')
                else:
                    print(". ", end='')
            print()
        print(f"{y} ", end='')
        for x in range(state.width):
            if x > 0:
                if ((x, y), Facing.WEST) in state.obstacles:
                    print("|", end='')
                else:
                    print(".", end='')
            print("O", end='')
        print()


def a_star(state, start, end):
    visited = {}
    frontier = [(0, manhattan_distance(start, end), start, None)]
    current = None
    while len(frontier) > 0:
        if current == end:
            path = []
            while current is not None:
                path = [current] + path
                current = visited[current]
            return path
        else:
            cost, estimate, current, parent = heapq.heappop(frontier)
            if current not in visited:
                visited[current] = parent
                for f in Facing:
                    n = f + current
                    if in_bounds(state, n) and (current, f) not in state.obstacles:
                        heapq.heappush(frontier, (cost + 1, manhattan_distance(n, end), n, current))


def make_grid_planner():
    p = Planner()
    p.declare_operators(move_one_step, turn_to)
    p.declare_methods(find_route)
    return p


if __name__ == '__main__':
    max_seconds = 4
    state, tasks = generate_grid_world(7, 7, (1, 0), Facing.NORTH, (2, 6), 30)
    optimal = a_star(state, (1, 0), (2, 6))
    show_grid(state)
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
