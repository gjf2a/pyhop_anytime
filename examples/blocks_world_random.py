from pyhop_anytime.pyhop import *

import blocks_world

planner = blocks_world.make_blocks_planner()

state3 = State('state3')
state3.pos = {1:12, 12:13, 13:'table', 11:10, 10:5, 5:4, 4:14, 14:15, 15:'table', 9:8, 8:7, 7:6, 6:'table', 19:18, 18:17, 17:16, 16:3, 3:2, 2:'table'}
state3.clear = {x:False for x in range(1,20)}
state3.clear.update({1:True, 11:True, 9:True, 19:True})
state3.holding = False

print(state3)
print('')

print("- Define goal3:")

goal3 = State('goal3')
goal3.pos = {15:13, 13:8, 8:9, 9:4, 4:'table', 12:2, 2:3, 3:16, 16:11, 11:7, 7:6, 6:'table'}
goal3.clear = {17:True, 15:True, 12:True}

plan = planner.randhop(state3, [('move_blocks', goal3)], verbose=3)
if plan is None:
    print("Failed to find plan")
else:
    print(plan[0])
    print(plan[1], len(plan[0]))

print("anyhop_random() for two seconds:")
plan_times = planner.anyhop_random(state3, [('move_blocks', goal3)], max_seconds=2.0)
print(f"{len(plan_times)} plans")
print([(plan[1], plan[2]) for plan in plan_times])

print("monte carlo (exhaustive) for 5 seconds:")
plan_times = planner.anyhop(state3, [('move_blocks', goal3)], max_seconds=5,
                            queue_init=lambda: MonteCarloPlannerHeap(planner, go_deep_first=False, show_progress=True))
print(f"{len(plan_times)} plans")
print([(plan[1], plan[2]) for plan in plan_times])

print("monte carlo (go_deep_first) for 5 seconds:")
plan_times = planner.anyhop(state3, [('move_blocks', goal3)], max_seconds=5,
                            queue_init=lambda: MonteCarloPlannerHeap(planner, go_deep_first=True, show_progress=True))
print(f"{len(plan_times)} plans")
print([(plan[1], plan[2]) for plan in plan_times])

print("monte carlo (exhaustive) for 5 seconds, 5 samples:")
plan_times = planner.anyhop(state3, [('move_blocks', goal3)], max_seconds=5,
                            queue_init=lambda: MonteCarloPlannerHeap(planner, num_samples=5, go_deep_first=False, show_progress=True))
print(f"{len(plan_times)} plans")
print([(plan[1], plan[2]) for plan in plan_times])

print("monte carlo (go_deep_first) for 5 seconds, 5 samples:")
plan_times = planner.anyhop(state3, [('move_blocks', goal3)], max_seconds=5,
                            queue_init=lambda: MonteCarloPlannerHeap(planner, num_samples=5, go_deep_first=True, show_progress=True))
print(f"{len(plan_times)} plans")
print([(plan[1], plan[2]) for plan in plan_times])
