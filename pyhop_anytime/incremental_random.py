import time


class IncrementalRandomTracker:
    def __init__(self, planner, tasks, state, min_avg_plan_step_count, show_incremental=False):
        self.planner = planner
        self.start_tasks = tasks
        self.start_state = state
        self.min_avg_plan_step_count = min_avg_plan_step_count
        self.show_incremental = show_incremental
        self.attempts = 0
        self.num_resets = -1
        self.full_reset()

    # noinspection PyAttributeOutsideInit
    def full_reset(self):
        self.num_resets += 1
        self.plan_prefix = []
        self.prefix_cost = 0
        self.state = self.start_state
        self.tasks = self.start_tasks
        self.partial_reset()

    # noinspection PyAttributeOutsideInit
    def partial_reset(self):
        self.first_action_outcomes = {}
        self.first_action_states = {}
        self.first_action_costs = {}
        self.first_action_tasks = {}
        self.current_first_actions = 0

    def log(self, msg):
        if self.show_incremental:
            print(msg)

    def plan(self, max_seconds, verbose=0):
        max_cost = None
        plan_times = []
        start_time = time.time()
        elapsed_time = 0
        while elapsed_time < max_seconds:
            plan_steps = self.planner.randhop_steps(self.state, self.tasks, verbose=verbose)
            elapsed_time = time.time() - start_time
            if plan_steps is None or len(plan_steps[-1].plan) == 0:
                self.min_avg_plan_step_count *= 2
                self.log(f"Reached end; updating min_avg_plan_step_count to {self.min_avg_plan_step_count}")
                self.full_reset()
            else:
                self.record_prefix(plan_steps)
                if self.ready_to_choose_prefix():
                    self.choose_best_prefix()
                self.attempts += 1
                current_total_cost = self.prefix_cost + plan_steps[-1].total_cost
                if max_cost is None or current_total_cost < max_cost:
                    plan_times.append(([self.plan_prefix] + plan_steps[-1].plan, current_total_cost, elapsed_time))
                    max_cost = current_total_cost
        return plan_times

    def progress_report(self):
        return f"Full resets: {self.num_resets} Prefix steps: {len(self.plan_prefix)}"

    def record_prefix(self, plan_steps):
        prefix = plan_steps[-1].plan[0]
        if prefix not in self.first_action_outcomes:
            self.first_action_outcomes[prefix] = OutcomeCounter()
            action_step = 0
            while plan_steps[action_step].tasks[0] != prefix:
                action_step += 1
            self.first_action_states[prefix] = plan_steps[action_step + 1].state
            self.first_action_costs[prefix] = plan_steps[action_step + 1].current_cost
            self.first_action_tasks[prefix] = plan_steps[action_step + 1].tasks
        self.first_action_outcomes[prefix].record(plan_steps[-1].total_cost + self.prefix_cost)
        self.current_first_actions += 1

    def ready_to_choose_prefix(self):
        return self.current_first_actions / len(self.first_action_outcomes) >= self.min_avg_plan_step_count

    # noinspection PyAttributeOutsideInit
    def choose_best_prefix(self):
        lowest_cost = None
        lowest_cost_step = None
        for (first_step, outcome) in self.first_action_outcomes.items():
            if lowest_cost is None or outcome.mean() < lowest_cost:
                lowest_cost_step = first_step
                lowest_cost = outcome.mean()
        self.plan_prefix.append(lowest_cost_step)
        self.log(f"chose {lowest_cost_step}")
        self.prefix_cost += self.first_action_costs[lowest_cost_step]
        self.state = self.first_action_states[lowest_cost_step]
        self.tasks = self.first_action_tasks[lowest_cost_step]
        self.partial_reset()


class OutcomeCounter:
    def __init__(self, total=0, count=0, min=None, max=None):
        self.total = total
        self.count = count
        self.min = min
        self.max = max

    def __str__(self):
        return f"{self.mean()} [{self.min}, {self.max}]"

    def __repr__(self):
        return f"OutcomeCounter(total={self.total}, count={self.count}, min={self.min}, max={self.max})"

    def record(self, outcome):
        self.total += outcome
        self.count += 1
        if self.min is None or self.min > outcome:
            self.min = outcome
        if self.max is None or self.max < outcome:
            self.max = outcome

    def mean(self):
        return self.total / self.count


class ActionTracker:
    def __init__(self, planner, tasks, state):
        self.planner = planner
        self.tasks = tasks
        self.state = state
        self.action_outcomes = {}

    def plan(self, max_seconds, verbose=0):
        start_time = time.time()
        elapsed_time = 0
        max_cost = None
        plan_times = []
        attempts = 0
        while elapsed_time < max_seconds:
            plan_step = self.planner.make_action_tracked_plan(self, verbose)
            elapsed_time = time.time() - start_time
            attempts += 1
            if plan_step is not None and (max_cost is None or plan_step.total_cost < max_cost):
                plan_times.append((plan_step.plan, plan_step.total_cost, elapsed_time))
                max_cost = plan_step.total_cost
        print(f"attempts: {attempts}")
        return plan_times
