import sys

from pyhop_anytime.hddl_parser import parse_hddl, Domain, Problem

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python3 hddl_planner.py domain.hddl problem.hddl max_seconds [-v=verbosity] [-p=(random_tracked | random | dfs)]")
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
                verbosity = 0
                for arg in sys.argv:
                    if arg.startswith("-v"):
                        verbosity = int(arg.split('=')[1])

                random_tracked = False
                random = False
                dfs = False
                for arg in sys.argv:
                    if arg.startswith('-p'):
                        planner_name = arg.split('=')[1]
                        random_tracked = random_tracked or planner_name == 'random_tracked'
                        random = random or planner_name == 'random'
                        dfs = dfs or planner_name == 'dfs'
                if not (random or dfs):
                    random_tracked = True

                if random_tracked:
                    plan_times = planner.anyhop_random_tracked(problem.init_state(), problem.init_tasks(), max_seconds, verbose=verbosity)
                    print("Random action tracked")
                    print(plan_times[-1])
                if random:
                    plan_times = planner.anyhop_random(problem.init_state(), problem.init_tasks(), max_seconds,
                                                       verbose=verbosity)
                    print("Random")
                    print(plan_times[-1])
                if dfs:
                    plan_times = planner.anyhop(problem.init_state(), problem.init_tasks(), max_seconds,
                                                verbose=verbosity)
                    print("DFS")
                    print(plan_times[-1])