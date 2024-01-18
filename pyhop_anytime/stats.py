from typing import List, Tuple
import statistics


def mean_and_bound(values: List[float], num_stdevs: int) -> Tuple[float, float]:
    xbar = statistics.mean(values)
    bound = num_stdevs * statistics.stdev(values, xbar)
    return xbar, bound


def report_mean_and_bound(values: List[float], num_stdevs: int) -> str:
    xbar, bound = mean_and_bound(values, num_stdevs)
    return f"{xbar:.2f} +/- {bound:.2f}"
