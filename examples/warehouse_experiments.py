from warehouse import *
from pyhop_anytime.pyhop import *

if __name__ == '__main__':
    planner = warehouse_planner()
    for i in range(10):
        print(f"Experiment {i + 1}")
        state, tasks = problem_generator(10, 10, 6)

        print("purely random")
        plan_times = planner.anyhop_random(state, tasks, max_seconds=1)
        print([(plan[1], plan[2]) for plan in plan_times])
        print()
        print("DFS")
        plan_times = planner.anyhop(state, tasks, max_seconds=5)
        print([(plan[1], plan[2]) for plan in plan_times])
        print()
        print("monte carlo")
        plan_times = planner.anyhop(state, tasks, max_seconds=10, queue_init=lambda: MonteCarloPlannerHeap(planner))
        print([(plan[1], plan[2]) for plan in plan_times])
        print()
        print()
