from typing import List, Tuple
import statistics


def mean_and_bound(values: List[float], num_stdevs: int) -> Tuple[float, float]:
    xbar = statistics.mean(values)
    bound = num_stdevs * statistics.stdev(values, xbar)
    return xbar, bound


def report_mean_bound(values: List[float], num_stdevs: int) -> str:
    xbar, bound = mean_and_bound(values, num_stdevs)
    return f"{xbar:.2f} +/- {bound:.2f}"


def lo_hi_bounds(values: List[float], num_stdevs: int) -> Tuple[float, float]:
    xbar, bound = mean_and_bound(values, num_stdevs)
    return xbar - bound, xbar + bound


def report_lo_hi_bounds(values: List[float], num_stdevs: int) -> str:
    lo, hi = lo_hi_bounds(values, num_stdevs)
    return f"({lo:.2f}, {hi:.2f})"
