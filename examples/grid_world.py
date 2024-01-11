import random
import heapq

from pyhop_anytime import State, TaskList, Planner, within, Facing, manhattan_distance, projection, \
    generate_grid_obstacles, a_star, show_grid


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


def generate_grid_world(width, height, start, start_facing, end, num_obstacles):
    state = State(f"grid_{width}x{height}_{start}_to_{end}_{num_obstacles}_obstacles")
    state.at = start
    state.facing = start_facing
    state.visited = {(start, start_facing)}
    state.width = width
    state.height = height
    state.just_turned = False
    state.obstacles = generate_grid_obstacles(width, height, num_obstacles)
    return state, [('find_route', start, start_facing, end)]


def make_grid_planner():
    p = Planner()
    p.declare_operators(move_one_step, turn_to)
    p.declare_methods(find_route)
    return p


if __name__ == '__main__':
    max_seconds = 4
    state, tasks = generate_grid_world(7, 7, (1, 0), Facing.NORTH, (2, 6), 30)
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
