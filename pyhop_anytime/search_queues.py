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
        if len(items) > 0:
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


class MonteCarloPlannerHeap:
    def __init__(self, planner, num_samples=10, show_progress=False):
        self.planner = planner
        self.num_samples = num_samples
        self.plan_step_heap = []
        self.show_progress = show_progress

    def enqueue_all_steps(self, items):
        for plan_step in items:
            options = self.planner.n_random(plan_step.state, plan_step.tasks, self.num_samples)
            costs = [plan[1] for plan in options]
            rating = sum(costs) / len(costs)
            heapq.heappush(self.plan_step_heap, RatedPlanStep(plan_step, rating))

    def dequeue_step(self):
        if self.show_progress:
            popped = heapq.heappop(self.plan_step_heap)
            print(f"From heap (depth {popped.step.depth()}) (rating: {popped.rating})\t", end='')
            if popped.step.complete():
                print("Complete!")
            else:
                print("In progress...")
            return popped.step
        else:
            return heapq.heappop(self.plan_step_heap).step

    def empty(self):
        return len(self.plan_step_heap) == 0


@total_ordering
class RatedPlanStep:
    def __init__(self, step, rating):
        self.step = step
        self.rating = rating

    def __lt__(self, other):
        return self.rating < other.rating

    def __eq__(self, other):
        return self.rating == other.rating
