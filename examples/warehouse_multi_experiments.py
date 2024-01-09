from warehouse_multi import *
from pyhop_anytime.pyhop import *
import sys

if __name__ == '__main__':
    num_packages = 3#18#3
    num_robots = 2
    max_seconds = 5
    for arg in sys.argv:
        if arg.startswith("-robot"):
            num_robots = int(arg.split(":")[1])
        elif arg.startswith("-packages"):
            num_packages = int(arg.split(":")[1])
        elif arg.startswith("-seconds"):
            max_seconds = int(arg.split(":")[1])

    planner = warehouse_planner()
    for i in range(10):
        print(f"Experiment {i + 1}")
        state, tasks = problem_generator(10, 10, num_packages, num_robots)
        tasks = [('nondeterministic_delivery', tasks)]

        print("DFS")
        plan_times = planner.anyhop(state, tasks, max_seconds=max_seconds)
        print([(plan[1], plan[2]) for plan in plan_times])
        print()
        print("purely random")
        plan_times = planner.anyhop_random(state, tasks, max_seconds=max_seconds)
        print([(plan[1], plan[2]) for plan in plan_times])
        print()
        print("incremental random")
        plan_times = planner.anyhop_random_incremental(state, tasks, max_seconds=max_seconds)
        print([(plan[1], plan[2]) for plan in plan_times])
        print()
        print("tracked random")
        plan_times = planner.anyhop_random_tracked(state, tasks, max_seconds=max_seconds)
        print([(plan[1], plan[2]) for plan in plan_times])
        print()
