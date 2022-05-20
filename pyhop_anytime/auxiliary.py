import sys


def anyhop_main(planner):
    if len(sys.argv) == 1:
        print(f"Usage: python3 {sys.argv[0]} -v:[verbosity] -s:[max seconds] [planner_file]+")
    else:
        anyhop_args(planner, sys.argv[1:])


def anyhop_args(planner, args):
    verbosity = find_verbosity(args)
    max_seconds = find_max_seconds(args)
    for filename in args:
        if not filename.startswith("-"):
            exec(open(filename).read())
            plans = planner.anyhop(state, [('start', goals)], max_seconds=max_seconds, verbose=verbosity)
            for (plan, time) in plans:
                print(plan)
            for (plan, time) in plans:
                print(f"Length: {len(plan)} time: {time}")
            print(len(plans), "total plans generated")


def find_verbosity(args):
    for arg in args:
        if arg.startswith("-v"):
            return int(arg.split(':')[1])
    return 1


def find_max_seconds(args):
    for arg in args:
        if arg.startswith("-s"):
            return int(arg.split(':')[1])