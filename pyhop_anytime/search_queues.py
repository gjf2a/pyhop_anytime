import heapq
from functools import total_ordering


class SearchStack:
    def __init__(self):
        self.stack = []

    def enqueue_all_steps(self, items):
        self.stack.extend(items)

    def dequeue_step(self):
        return self.stack.pop()

    def empty(self):
        return len(self.stack) == 0


@total_ordering
class WrappedPlanStep:
    def __init__(self, step):
        self.step = step

    def __lt__(self, other):
        return self.step.total_cost < other.step.total_cost

    def __eq__(self, other):
        return self.step.total_cost == other.step.total_cost


class HybridQueue:
    def __init__(self):
        self.heap = []
        self.next_pop = None

    def enqueue_all_steps(self, items):
        self.enqueue_all([WrappedPlanStep(item) for item in items])

    def dequeue_step(self):
        d = self.dequeue()
        if d: return d.step

    def empty(self):
        return len(self.heap) == 0 and self.next_pop is None

    def enqueue_all(self, items):
        if self.next_pop:
            assert False
        for item in items[:-1]:
            heapq.heappush(self.heap, item)
        self.next_pop = items[-1]

    def dequeue(self):
        if self.next_pop:
            result = self.next_pop
            self.next_pop = None
            return result
        elif self.heap:
            return heapq.heappop(self.heap)