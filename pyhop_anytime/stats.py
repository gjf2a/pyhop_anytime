from typing import List, Tuple
import statistics


def mean_and_bounds(values: List[float], num_stdevs: int) -> Tuple[float, float]:
    xbar = statistics.mean(values)
    bound = num_stdevs * statistics.stdev(values, xbar)
    return xbar, bound
