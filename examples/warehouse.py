from pyhop_anytime import State, TaskList, Planner


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
    if state.loc[entity] == start and manhattan_distance(start, end) == 1:
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


def find_route(state, entity, start, end):
    current_distance = manhattan_distance(start, end)
    if start == end:
        return TaskList(completed=True)
    elif current_distance == 1:
        return TaskList([('go', entity, start, end)])
    else:
        return TaskList([[('go', entity, start, neighbor),
                          ('find_route', entity, neighbor, end)]
                         for neighbor in manhattan_neighbors(start)
                         if manhattan_distance(neighbor, end) < current_distance])


def deliver(state, item, end):
    if state.loc[item] == end:
        return TaskList(completed=True)
    else:
        return TaskList([('find_route', 'robot1', state.loc['robot1'], state.loc[item]),
                         ('pick_up', 'robot1', item),
                         ('find_route', 'robot1', state.loc[item], end),
                         ('put_down', 'robot1', item)])


if __name__ == '__main__':
    planner = Planner()
    planner.declare_operators(go, pick_up, put_down)
    planner.declare_methods(find_route, deliver)

    state = State('3rd-floor')
    state.robots = ['robot1']
    state.loc = {'robot1': (0, 0), 'package1': (-2, 1), 'package2': (-1, 1)}

    print(planner.anyhop(state, [('deliver', 'package1', (0, 0))]))
