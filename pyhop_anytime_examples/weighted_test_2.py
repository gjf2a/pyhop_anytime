from pyhop_anytime import State
from pyhop_anytime_examples.tsp import tsp_planner

p = tsp_planner()
s = State("tsp_4_cities_10x10")
s.locations = [(-3.3495668776048957, -0.9110076696952882), (0.9836015543687253, -1.882769548407781), (-2.4352073793633187, 4.66846054967948), (-0.8003205578696644, -2.8611353845895704)]
s.distances = [[0.0, 4.440796078269251, 5.65389413617178, 3.2096191211859413], [4.440796078269251, 0.0, 7.389646156850168, 2.0345952452369414], [5.65389413617178, 7.389646156850168, 0.0, 7.705041846249418], [3.2096191211859413, 2.0345952452369414, 7.705041846249418, 0.0]]
s.at = 0
s.visited = {}

t = [('nondeterministic_choice',)]

all_solutions = p.anyhop(s, t, disable_branch_bound=True)
for solution in all_solutions:
    print(solution)
print("Weighted random")
weighted_solutions = p.anyhop_weighted_random(s, t, max_seconds=1)
for solution in weighted_solutions:
    print(solution)