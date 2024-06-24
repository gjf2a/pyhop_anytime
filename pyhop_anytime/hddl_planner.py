import sys

from pyhop_anytime.hddl_parser import parse_hddl, Domain, Problem

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python3 hddl_planner.py domain.hddl problem.hddl max_seconds")
    else:
        with open(sys.argv[1]) as domain_file:
            domain = parse_hddl(domain_file.read())
            assert type(domain) == Domain
            with open(sys.argv[2]) as problem_file:
                problem = parse_hddl(problem_file.read())
                assert type(problem) == Problem
                print("tasks", [(k, len(domain.task2methods[k])) for k in domain.task2methods.keys()])
                planner = domain.make_planner()
                planner.print_methods()
                max_seconds = float(sys.argv[3])
                plan_times = planner.anyhop_random_tracked(problem.init_state(), problem.init_tasks(), max_seconds)
                print(plan_times[-1])