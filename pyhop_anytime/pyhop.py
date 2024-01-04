"""
This is a derived work of the Pyhop planner written by Dana Nau.

Alterations are authored by Gabriel Ferrer.

It incorporates the anytime planning algorithm from SHOP3
(https://github.com/shop-planner/shop3).

This software is adapted from:

Pyhop, version 1.2.2 -- a simple SHOP-like planner written in Python.
Author: Dana S. Nau, 2013.05.31

Copyright 2013 Dana S. Nau - http://www.cs.umd.edu/~nau

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import copy
import time
from pyhop_anytime.search_queues import *
import random


class State:
    def __init__(self, name):
        self.__name__ = name

    def __repr__(self):
        return '\n'.join([f"{self.__name__}.{name} = {val}" for (name, val) in vars(self).items() if name != "__name__"])


class TaskList:
    def __init__(self, options=None, completed=False):
        self.completed = completed
        if options and len(options) > 0:
            self.options = options if type(options[0]) == list else [options]
        else:
            self.options = [[]] if completed else []

    def __repr__(self):
        return f"TaskList(options={self.options},completed={self.completed})"

    def add_option(self, option):
        self.options.append(option)

    def add_options(self, option_seq):
        for option in option_seq:
            self.add_option(option)

    def complete(self):
        return self.completed

    def failed(self):
        return len(self.options) == 0 and not self.completed

    def in_progress(self):
        return not self.complete() and not self.failed()


class Planner:
    def __init__(self, verbose=0, copy_func=copy.deepcopy, cost_func=lambda state, step: 1):
        self.copy_func = copy_func
        self.cost_func = cost_func
        self.operators = {}
        self.methods = {}
        self.verbose = verbose

    def declare_operators(self, *op_list):
        self.operators.update({op.__name__:op for op in op_list})

    def declare_methods(self, *method_list):
        self.methods.update({method.__name__:method for method in method_list})

    def print_operators(self):
        print(f'OPERATORS: {", ".join(self.operators)}')

    def print_methods(self):
        print(f'METHODS: {", ".join(self.methods)}')

    def log(self, min_verbose, msg):
        if self.verbose >= min_verbose:
            print(msg)

    def log_state(self, min_verbose, msg, state):
        if self.verbose >= min_verbose:
            print(msg)
            print(state)

    def pyhop(self, state, tasks, verbose=0):
        for plan in self.pyhop_generator(state, tasks, verbose):
            if plan:
                return plan

    def anyhop(self, state, tasks, max_seconds=None, verbose=0, disable_branch_bound=False, queue_init=lambda: SearchStack()):
        start_time = time.time()
        plan_times = []
        for plan in self.pyhop_generator(state, tasks, verbose, disable_branch_bound, yield_cost=True,
                                         queue_init=queue_init):
            elapsed_time = time.time() - start_time
            if max_seconds and elapsed_time > max_seconds:
                break
            if plan:
                plan_times.append((plan[0], plan[1], elapsed_time))
        return plan_times

    def pyhop_generator(self, state, tasks, verbose=0, disable_branch_bound=False, yield_cost=False,
                        queue_init=lambda: SearchStack()):
        self.verbose = verbose
        self.log(1, f"** anyhop, verbose={self.verbose}: **\n   state = {state.__name__}\n   tasks = {tasks}")
        options = queue_init()
        options.enqueue_all_steps([PlanStep([], tasks, state, self.copy_func, self.cost_func)])
        lowest_cost = None
        while not options.empty():
            candidate = options.dequeue_step()
            if disable_branch_bound or lowest_cost is None or candidate.total_cost < lowest_cost:
                self.log(2, f"depth {candidate.depth()} tasks {candidate.tasks}")
                self.log(3, f"plan: {candidate.plan}")
                if candidate.complete():
                    self.log(3, f"depth {candidate.depth()} returns plan {candidate.plan}")
                    self.log(1, f"** result = {candidate.plan}\n")
                    lowest_cost = candidate.total_cost
                    if yield_cost:
                        yield candidate.plan, candidate.total_cost
                    else:
                        yield candidate.plan
                else:
                    options.enqueue_all_steps(candidate.successors(self))
                    yield None
            else:
                yield None

    def anyhop_best(self, state, tasks, max_seconds=None, verbose=0):
        plans = self.anyhop(state, tasks, max_seconds, verbose)
        return plans[-1][0]

    def anyhop_stats(self, state, tasks, max_seconds=None, verbose=0):
        plans = self.anyhop(state, tasks, max_seconds, verbose)
        return [(len(plan), cost, tm) for (plan, cost, tm) in plans]

    def randhop(self, state, tasks, max_cost=None, verbose=0):
        self.verbose = verbose
        candidate = PlanStep([], tasks, state, self.copy_func, self.cost_func)
        while not (candidate is None or candidate.complete()):
            successors = candidate.successors(self)
            if len(successors) == 0 or max_cost is not None and candidate.total_cost >= max_cost:
                return None
            candidate = successors[random.randint(0, len(successors) - 1)]
        return candidate

    def weighted_randhop_steps(self, state, tasks, step_costs, show, max_cost=None, verbose=0):
        self.verbose = verbose
        steps = [PlanStep([], tasks, state, self.copy_func, self.cost_func)]
        while not (steps[-1] is None or steps[-1].complete()):
            successors = steps[-1].successors(self)
            if len(successors) == 0 or max_cost is not None and steps[-1].total_cost >= max_cost:
                return None
            steps.append(step_costs.random_pick_from(successors, show))
        return steps

    def anyhop_weighted_random(self, state, tasks, max_seconds, show=False, verbose=0):
        start_time = time.time()
        elapsed_time = 0
        max_cost = None
        plan_times = []
        step_costs = PlanStepTable()
        attempts = 0
        while elapsed_time < max_seconds:
            plan_steps = self.weighted_randhop_steps(state, tasks, step_costs, show, verbose=verbose)
            elapsed_time = time.time() - start_time
            attempts += 1
            final_plan_step = plan_steps[-1]
            if final_plan_step is not None:
                for plan_step in plan_steps:
                    step_costs.add(plan_step, final_plan_step.total_cost - plan_step.total_cost)
                if max_cost is None or final_plan_step.total_cost < max_cost:
                    plan_times.append((final_plan_step.plan, final_plan_step.total_cost, elapsed_time))
                    max_cost = final_plan_step.total_cost
        return plan_times

    def anyhop_random(self, state, tasks, max_seconds, use_max_cost=True, verbose=0):
        start_time = time.time()
        elapsed_time = 0
        max_cost = None
        plan_times = []
        attempts = 0
        while elapsed_time < max_seconds:
            if use_max_cost:
                plan_step = self.randhop(state, tasks, max_cost=max_cost, verbose=verbose)
            else:
                plan_step = self.randhop(state, tasks, verbose=verbose)
            elapsed_time = time.time() - start_time
            attempts += 1
            if plan_step is not None and (max_cost is None or plan_step.total_cost < max_cost):
                plan_times.append((plan_step.plan, plan_step.total_cost, elapsed_time))
                max_cost = plan_step.total_cost
        return plan_times

    def n_random(self, state, tasks, n, verbose=0):
        self.verbose = verbose
        plans = []
        for i in range(n):
            plan = self.randhop(state, tasks)
            if plan is not None:
                plans.append(plan)
        return plans


class PlanStep:
    def __init__(self, plan, tasks, state, copy_func, cost_func, current_cost=0, past_cost=0):
        self.copy_func = copy_func
        self.cost_func = cost_func
        self.plan = plan
        self.tasks = tasks
        self.state = state
        self.total_cost = past_cost + current_cost
        self.current_cost = current_cost

    def depth(self):
        return len(self.plan)

    def complete(self):
        return len(self.tasks) == 0

    def successors(self, planner):
        options = []
        self.add_operator_options(options, planner)
        self.add_method_options(options, planner)
        if len(options) == 0:
            planner.log(3, f"depth {self.depth()} returns failure")
        return options

    def add_operator_options(self, options, planner):
        next_task = self.next_task()
        if type(next_task[0]) == list:
            print(f"next_task: {next_task}")
        if next_task[0] in planner.operators:
            planner.log(3, f"depth {self.depth()} action {next_task}")
            operator = planner.operators[next_task[0]]
            newstate = operator(self.copy_func(self.state), *next_task[1:])
            planner.log_state(3, f"depth {self.depth()} new state:", newstate)
            if newstate:
                options.append(PlanStep(self.plan + [next_task], self.tasks[1:], newstate, self.copy_func,
                                        self.cost_func, past_cost=self.total_cost,
                                        current_cost=self.cost_func(self.state, next_task)))

    def add_method_options(self, options, planner):
        next_task = self.next_task()
        if next_task[0] in planner.methods:
            planner.log(3, f"depth {self.depth()} method instance {next_task}")
            method = planner.methods[next_task[0]]
            subtask_options = method(self.state, *next_task[1:])
            if subtask_options is not None:
                for subtasks in subtask_options.options:
                    planner.log(3, f"depth {self.depth()} new tasks: {subtasks}")
                    options.append(PlanStep(self.plan, subtasks + self.tasks[1:], self.state, self.copy_func, self.cost_func, past_cost=self.total_cost))

    def next_task(self):
        result = self.tasks[0]
        if type(result) is tuple:
            return result
        else:
            return tuple([result])


def plan_step_key(plan_step):
    return f"{plan_step.state}:{plan_step.tasks}"


class OutcomeCounter:
    def __init__(self):
        self.total = 0
        self.count = 0
        self.min = None
        self.max = None

    def __str__(self):
        return f"{self.mean()} [{self.min}, {self.max}]"

    def record(self, outcome):
        self.total += outcome
        self.count += 1
        if self.min is None or self.min > outcome:
            self.min = outcome
        if self.max is None or self.max < outcome:
            self.max = outcome

    def mean(self):
        return self.total / self.count


class PlanStepTable:
    def __init__(self):
        self.table = {}

    def add(self, plan_step, final_plan_cost):
        key = plan_step_key(plan_step)
        if key not in self.table:
            self.table[key] = OutcomeCounter()
        self.table[key].record(final_plan_cost)

    def cost_for(self, plan_step):
        return self.table.get(plan_step_key(plan_step))

    def random_pick_from(self, successors, show):
        if len(successors) == 1:
            return successors[0]
        d = self.distribution_for(successors)
        for i in range(len(successors)):
            for j in range(i + 1, len(successors)):
                if d[i] != d[j]:
                    show = True
        if show:
            print("Successor tasks")
            for s in successors:
                print(f"Plan: {s.plan} Tasks: {s.tasks}")
            print("distribution")
            print(d)
        r = random.random()
        if show: print(f"starting r: {r}")
        for (i, share) in d.items():
            if show: print(f"{i} {share}")
            if share > r:
                if show: print("returning")
                return successors[i]
            else:
                r -= share
                if show: print(f"Updated r: {r}")
        assert False

    def distribution_for(self, successors):
        outcomes = [self.cost_for(s) for s in successors]
        rankable = {i for i in range(len(outcomes)) if outcomes[i] is not None}
        if len(rankable) > 1:
            rankings = [(outcomes[i].mean(), i) for i in rankable]
            rankings.sort(key=lambda k: k[0])
            rankable_budget = len(rankable) / len(outcomes)
            distribution = {}
            if len(rankable) < len(outcomes):
                unrankable_share = (1.0 - rankable_budget) / (len(outcomes) - len(rankable))
                for i in range(len(outcomes)):
                    if i not in rankable:
                        distribution[i] = unrankable_share
            rankable_share = 2 * rankable_budget / (len(rankings) * (len(rankings) + 1))
            for (r_i, (m, i)) in enumerate(rankings):
                distribution[i] = rankable_share * (len(rankings) - r_i)
            assert len(distribution) == len(successors)
            return distribution
        else:
            share = 1.0 / len(successors)
            return {i: share for i in range(len(successors))}


############################################################
# Helper functions that may be useful in domain models


def forall(seq,cond):
    """True if cond(x) holds for all x in seq, otherwise False."""
    for x in seq:
        if not cond(x): return False
    return True


def find_if(cond,seq):
    """
    Return the first x in seq such that cond(x) holds, if there is one.
    Otherwise return None.
    """
    for x in seq:
        if cond(x):
            return x
