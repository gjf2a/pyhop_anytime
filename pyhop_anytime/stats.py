from typing import List, Tuple, Dict
import statistics


def mean_and_bound(values: List[float], num_stdevs: int) -> Tuple[float, float]:
    xbar = statistics.mean(values)
    bound = num_stdevs * statistics.stdev(values, xbar)
    return xbar, bound


def report_mean_and_bound(values: List[float], num_stdevs: int) -> str:
    xbar, bound = mean_and_bound(values, num_stdevs)
    return f"{xbar:.2f} +/- {bound:.2f}"


def lo_hi_bounds(values: List[float], num_stdevs: int) -> Tuple[float, float, float]:
    xbar, bound = mean_and_bound(values, num_stdevs)
    return xbar - bound, xbar, xbar + bound


def report_lo_hi_bounds(values: List[float], num_stdevs: int) -> str:
    lo, mean, hi = lo_hi_bounds(values, num_stdevs)
    return f"({lo:.2f}, {mean:.2f}, {hi:.2f})"


def report_one(label, plan_times):
    print(label)
    print(f"{len(plan_times)} plans")
    if len(plan_times) > 0:
        print(f"steps: {plan_times[-1][1]:.2f} ({plan_times[-1][2]:.2f}s)")
        print()
        return plan_times[-1][1]


def experiment(num_problems: int, runs_per_problem: int, max_seconds: float, problem_generator,
               non_random_planners: Dict,
               random_planners: Dict):
    for i in range(num_problems):
        print(f"Problem {i + 1}")
        state, tasks = problem_generator()
        non_random_costs = {}
        for name, planner in non_random_planners.items():
            plan_times = planner(state, tasks, max_seconds)
            cost = report_one(name, plan_times)
            if cost is not None:
                non_random_costs[name] = cost

        random_costs = {}
        for name, planner in random_planners.items():
            random_costs[name] = []
            for j in range(runs_per_problem):
                print(f"Run {j + 1}")
                plan_times = planner(state, tasks, max_seconds)
                cost = report_one(name, plan_times)
                if cost is not None:
                    random_costs[name].append(cost)

        print(f"Problem {i + 1} summary")
        longest_name_len = max(len(name) for name in non_random_costs)
        longest_name_len = max(longest_name_len, max(len(name) for name in random_costs))
        for name, cost in non_random_costs.items():
            print(f"{name}:{' ' * (longest_name_len - len(name))}{cost}")
        for name, costs in random_costs.items():
            print(f"{name}:{' ' * (longest_name_len - len(name))}{report_lo_hi_bounds(costs, 2)}")
        print()
        print()