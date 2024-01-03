# Multi-robot version of the warehouse domain

from pyhop_anytime import State, TaskList, Planner
import random


def manhattan_distance(p1, p2):
    return sum(abs(p1[i] - p2[i]) for i in range(len(p1)))


def occupied(state, location):
    if hasattr(state, 'robots'):
        for robot in state.robots:
            if state.loc[robot] == location:
                return True
    return False


def manhattan_neighbors(p):
    return [(p[0] + offset[0], p[1] + offset[1]) for offset in ((-1, 0), (1, 0), (0, -1), (0, 1))]


def grid_world_plan_valid(planner, start_state, plan, tasks):
    current_state = prev_state = start_state
    for step in plan:
        current_state = planner.copy_func(prev_state)
        current_state = planner.operators[step[0]](current_state, *step[1:])
        if current_state is None:
            return False
        robot = step[1]
        if step[0] == 'go':
            if occupied(prev_state, step[3]) or prev_state.loc[robot] != step[2] or current_state.loc[robot] != step[3] or manhattan_distance(step[2], step[3]) != 1:
                return False
        elif step[0] == 'pick_up':
            if prev_state.loc[robot] != prev_state.loc[step[2]] or current_state.loc[step[2]] != robot:
                return False
        elif step[0] == 'put_down':
            if prev_state.loc[step[2]] != robot or current_state.loc[step[2]] != current_state.loc[robot]:
                return False
        prev_state = current_state
    for task in tasks:
        if current_state.loc[task[-2]] != task[-1]:
            return False
    return True


def go(state, entity, start, end):
    if not occupied(state, end) and state.loc[entity] == start and manhattan_distance(start, end) == 1:
        state.loc[entity] = end
        return state


def pick_up(state, bot, item):
    if state.loc[bot] == state.loc[item]:
        state.loc[item] = bot
        return state


def put_down(state, bot, item):
    if state.loc[item] == bot:
        state.loc[item] = state.loc[bot]
        return state


def deliver(state, item, end):
    if state.loc[item] == end:
        return TaskList(completed=True)
    else:
        task_list = []
        for entity in state.robots:
            task_list.append([('find_route', entity, state.loc[entity], state.loc[item]),
                              ('pick_up', entity, item),
                              ('find_route', entity, state.loc[item], end),
                              ('put_down', entity, item)])
        return TaskList(task_list)


def find_route(state, entity, start, end):
    current_distance = manhattan_distance(start, end)
    if start == end:
        return TaskList(completed=True)
    elif current_distance == 1 and not occupied(state, end):
        return TaskList([('go', entity, start, end)])
    else:
        return TaskList([[('go', entity, start, neighbor),
                          ('find_route', entity, neighbor, end)]
                         for neighbor in manhattan_neighbors(start)
                         if manhattan_distance(neighbor, end) < current_distance])


def random_coord(width, height):
    return random.randint(0, width), random.randint(0, height)


def problem_generator(width, height, num_packages, num_robots):
    state = State('3rd-floor')
    state.loc = {}
    state.robots = []
    for robot in range(num_robots):
        name = f'robot{robot + 1}'
        state.robots.append(name)
        state.loc[name] = random_coord(width, height)
    tasks = []
    for package in range(num_packages):
        name = f'package{package + 1}'
        start = random_coord(width, height)
        goal = random_coord(width, height)
        state.loc[name] = start
        tasks.append(('deliver', name, goal))
    return state, tasks


def nondeterministic_delivery(state, tasks):
    if len(tasks) == 0:
        return TaskList(completed=True)
    else:
        tlist = []
        for i in range(len(tasks)):
            task = tasks[i]
            others = tasks[:i] + tasks[i+1:]
            tlist.append([task, ('nondeterministic_delivery', others)])
        return TaskList(tlist)


def warehouse_planner():
    planner = Planner()
    planner.declare_operators(go, pick_up, put_down)
    planner.declare_methods(find_route, deliver)
    return planner


if __name__ == '__main__':
    planner = warehouse_planner()
    state = State('3rd-floor')
    state.robots = ['robot1']
    state.loc = {'robot1': (0, 0), 'package1': (-2, 1), 'package2': (-1, 1)}

    print(planner.anyhop(state, [('deliver', 'package1', (0, 0))]))
