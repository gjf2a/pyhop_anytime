from pyhop_anytime_examples.tsp import tsp_planner, make_metric_tsp_state

p = tsp_planner()
s, t = make_metric_tsp_state(4, 10, 10)
print(t)
print(s)
all_solutions = p.anyhop(s, t, disable_branch_bound=True)
for solution in all_solutions:
    print(solution)
print("Weighted random")
weighted_solutions = p.anyhop_weighted_random(s, t, max_seconds=1)
for solution in weighted_solutions:
    print(solution)