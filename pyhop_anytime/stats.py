import time
from typing import *
import numpy as np
import scipy.stats as st


def report_one(label: str, plan_times) -> float:
    print(label)
    print(f"{len(plan_times)} plans")
    if len(plan_times) > 0:
        print(f"steps: {plan_times[-1][1]:.2f} ({plan_times[-1][2]:.2f}s)")
        print()
        return plan_times[-1][1]


def get_confidence_interval(values: List[float]) -> Tuple[float, float, float]:
    # From https://scales.arabpsychology.com/stats/calculate-confidence-intervals-in-python/
    mean = np.mean(values)
    if len(values) < 30:
        lo, hi = st.t.interval(0.95, df=len(values) - 1, loc=mean, scale=st.sem(values))
    else:
        lo, hi = st.norm.interval(0.95, df=len(values) - 1, loc=mean, scale=st.sem(values))
    return lo, mean, hi


def report_confidence_interval(values: List[float]):
    lo, mean, hi = get_confidence_interval(values)
    return f"95% confidence interval: ({lo:.2f}, {mean:.2f}, {hi:.2f})"


def experiment(num_problems: int, runs_per_problem: int, max_seconds: float, problem_generator,
               non_random_planners: Dict,
               random_planners: Dict) -> Dict[str, np.ndarray]:
    result = {}
    for name in list(non_random_planners) + list(random_planners):
        result[name] = np.zeros((num_problems, 2))
    start_time = time.time()
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
            result[name][i][0] = cost
            result[name][i][1] = 0
        for name, costs in random_costs.items():
            print(f"{name}:{' ' * (longest_name_len - len(name))}{report_confidence_interval(costs)}")
            lo, mean, hi = get_confidence_interval(costs)
            result[name][i][0] = mean
            result[name][i][1] = hi - mean

        print()
        print()
    duration = time.time() - start_time
    print(f"Duration: {duration:.2f}s")
    return result
