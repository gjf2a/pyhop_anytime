from warehouse_multi import *
from pyhop_anytime.pyhop import *
import sys

if __name__ == '__main__':
    num_packages = 3
    num_robots = 2
    max_seconds = 3
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

        print("purely random")
        plan_times = planner.anyhop_random(state, tasks, max_seconds=max_seconds)
        print([(plan[1], plan[2]) for plan in plan_times])
        print()
        print("DFS")
        plan_times = planner.anyhop(state, tasks, max_seconds=max_seconds)
        print([(plan[1], plan[2]) for plan in plan_times])
        print()
        print("monte carlo go_deep")
        plan_times = planner.anyhop(state, tasks, max_seconds=max_seconds,
                                    queue_init=lambda: MonteCarloPlannerHeap(planner, go_deep_first=True))
        print([(plan[1], plan[2]) for plan in plan_times])
        print()
        print("monte carlo")
        plan_times = planner.anyhop(state, tasks, max_seconds=max_seconds,
                                    queue_init=lambda: MonteCarloPlannerHeap(planner, go_deep_first=False))
        print([(plan[1], plan[2]) for plan in plan_times])
        print()
        print()
