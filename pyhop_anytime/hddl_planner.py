import sys

from pyhop_anytime.hddl_parser import parse_hddl, Domain, Problem, UntypedSymbol

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
                # Test code
                state = problem.init_state()
                for symbol in [UntypedSymbol('clear', True, ['b3']), UntypedSymbol('done', False, ['b3']), UntypedSymbol('on-table', False, ['b3'])]:
                    print(symbol, symbol in state)
                plan_times = planner.anyhop(problem.init_state(), problem.init_tasks(), max_seconds, verbose=3)
                print(plan_times[-1])