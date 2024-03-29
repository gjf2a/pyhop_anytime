"""
Blocks-world test data for Pyhop 1.1.
Author: Dana Nau <nau@cs.umd.edu>, November 15, 2012
This file should work correctly in both Python 2.7 and Python 3.2.
"""
import unittest

from pyhop_anytime.pyhop import *

import blocks_world

planner = blocks_world.make_blocks_planner()
print('')
planner.print_operators()
print('')
planner.print_methods()

#############     beginning of tests     ################


print("""
****************************************
First, test pyhop on some of the operators and smaller tasks
****************************************
""")

print("- Define state1: a on b, b on table, c on table")

"""
A state is a collection of all of the state variables and their values. Every state variable in the domain should have a value.
"""

state1 = State('state1')
state1.pos = {'a': 'b', 'b': 'table', 'c': 'table'}
state1.clear = {'c': True, 'b': False, 'a': True}
state1.holding = False

print(state1)
print('')

print('- these should fail:')
planner.pyhop(state1, [('pickup', 'a')], verbose=1)
planner.pyhop(state1, [('pickup', 'b')], verbose=1)
print('- these should succeed:')
planner.pyhop(state1, [('pickup', 'c')], verbose=1)
planner.pyhop(state1, [('unstack', 'a', 'b')], verbose=1)
planner.pyhop(state1, [('get', 'a')], verbose=1)
print('- this should fail:')
planner.pyhop(state1, [('get', 'b')], verbose=1)
print('- this should succeed:')
planner.pyhop(state1, [('get', 'c')], verbose=1)

print("""
****************************************
Run pyhop on two block-stacking problems, both of which start in state1.
The goal for the 2nd problem omits some of the conditions in the goal
of the 1st problemk, but those conditions will need to be achieved
anyway, so both goals should produce the same plan.
****************************************
""")

print("- Define goal1a:")

"""
A goal is a collection of some (but not necessarily all) of the state variables and their desired values. Below, both goal1a and goal1b specify c on b, and b on a. The difference is that goal1a also specifies that a is on table and the hand is empty.
"""

goal1a = State('goal1a')
goal1a.pos = {'c': 'b', 'b': 'a', 'a': 'table'}
goal1a.clear = {'c': True, 'b': False, 'a': False}
goal1a.holding = False

print(goal1a)
print('')

print("- Define goal1b:")

goal1b = State('goal1b')
goal1b.pos = {'c': 'b', 'b': 'a'}

print(goal1b)

### goal1b omits some of the conditions of goal1a,
### but those conditions will need to be achieved anyway


planner.pyhop(state1, [('move_blocks', goal1a)], verbose=1)
planner.pyhop(state1, [('move_blocks', goal1b)], verbose=1)

print("""
****************************************
Run pyhop on two more planning problems. As before, the 2nd goal omits
some of the conditions in the 1st goal, but both goals should produce
the same plan.
****************************************
""")

print("- Define state 2:")

state2 = State('state2')
state2.pos = {'a': 'c', 'b': 'd', 'c': 'table', 'd': 'table'}
state2.clear = {'a': True, 'c': False, 'b': True, 'd': False}
state2.holding = False

print(state2)
print('')

print("- Define goal2a:")

goal2a = State('goal2a')
goal2a.pos = {'b': 'c', 'a': 'd', 'c': 'table', 'd': 'table'}
goal2a.clear = {'a': True, 'c': False, 'b': True, 'd': False}
goal2a.holding = False

print(goal2a)
print('')

print("- Define goal2b:")

goal2b = State('goal2b')
goal2b.pos = {'b': 'c', 'a': 'd'}

print(goal2b)
print('')

### goal2b omits some of the conditions of goal2a,
### but those conditions will need to be achieved anyway.

planner.pyhop(state2, [('move_blocks', goal2a)], verbose=1)
planner.pyhop(state2, [('move_blocks', goal2b)], verbose=1)

print("""
****************************************
Test pyhop on planning problem bw_large_d from the SHOP distribution.
****************************************
""")

print("- Define state3:")

state3 = State('state3')
state3.pos = {1: 12, 12: 13, 13: 'table', 11: 10, 10: 5, 5: 4, 4: 14, 14: 15, 15: 'table', 9: 8, 8: 7, 7: 6, 6: 'table',
              19: 18, 18: 17, 17: 16, 16: 3, 3: 2, 2: 'table'}
state3.clear = {x: False for x in range(1, 20)}
state3.clear.update({1: True, 11: True, 9: True, 19: True})
state3.holding = False

print(state3)
print('')

print("- Define goal3:")

goal3 = State('goal3')
goal3.pos = {15: 13, 13: 8, 8: 9, 9: 4, 4: 'table', 12: 2, 2: 3, 3: 16, 16: 11, 11: 7, 7: 6, 6: 'table'}
goal3.clear = {17: True, 15: True, 12: True}

print(goal3)
print('')

big_plan = planner.pyhop(state3, [('move_blocks', goal3)], verbose=3)
print(big_plan)

big_plan_stats = planner.anyhop_stats(state3, [('move_blocks', goal3)])
print("Plan lengths from anytime planner, including discovery times:")
print(big_plan_stats)

rand_plan = planner.randhop(state3, [('move_blocks', goal3)])
print(f"Random plan length: {len(rand_plan.plan)}")

rand_plan_times = planner.anyhop_random_incremental(state3, [('move_blocks', goal3)], 2)
print(f"Random incremental plan length: {len(rand_plan_times[-1][0])}")


class Test(unittest.TestCase):

    def test(self):
        plan = planner.pyhop(state3, [('move_blocks', goal3)])
        self.assertEqual(plan,
                         [('unstack', 1, 12), ('putdown', 1), ('unstack', 19, 18), ('putdown', 19), ('unstack', 18, 17),
                          ('putdown', 18), ('unstack', 17, 16), ('putdown', 17), ('unstack', 16, 3), ('putdown', 16),
                          ('unstack', 12, 13), ('putdown', 12), ('unstack', 11, 10), ('putdown', 11),
                          ('unstack', 10, 5), ('putdown', 10), ('unstack', 5, 4), ('putdown', 5), ('unstack', 4, 14),
                          ('putdown', 4), ('unstack', 9, 8), ('stack', 9, 4), ('unstack', 8, 7), ('stack', 8, 9),
                          ('pickup', 11), ('stack', 11, 7), ('pickup', 13), ('stack', 13, 8), ('unstack', 14, 15),
                          ('putdown', 14), ('pickup', 15), ('stack', 15, 13), ('pickup', 16), ('stack', 16, 11),
                          ('unstack', 3, 2), ('stack', 3, 16), ('pickup', 2), ('stack', 2, 3), ('pickup', 12),
                          ('stack', 12, 2)])


if __name__ == '__main__':
    unittest.main()
