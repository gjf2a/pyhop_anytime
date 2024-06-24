import unittest

from pyhop_anytime.hddl_parser import State, UntypedSymbol, Parameter


class MyTestCase(unittest.TestCase):
    def test_bug_1(self):
        state = State('pfile_005', [Parameter('b2', 'BLOCK'), Parameter('b5', 'BLOCK'), Parameter('b1', 'BLOCK'), Parameter('b3', 'BLOCK'), Parameter('b4', 'BLOCK')],
                      {UntypedSymbol('goal_on-table', True, ('b3',)), UntypedSymbol('goal_clear', True, ('b2',)),
                       UntypedSymbol('on-table', True, ('b4',)), UntypedSymbol('done', True, ('b3',)),
                       UntypedSymbol('clear', True, ('b5',)), UntypedSymbol('clear', True, ('b1',)),
                       UntypedSymbol('clear', True, ('b2',)), UntypedSymbol('done', True, ('b4',)),
                       UntypedSymbol('clear', True, ('b4',)), UntypedSymbol('goal_on', True, ('b5', 'b4')),
                       UntypedSymbol('goal_clear', True, ('b1',)), UntypedSymbol('goal_on-table', True, ('b4',)),
                       UntypedSymbol('on-table', True, ('b5',)), UntypedSymbol('done', True, ('b1',)),
                       UntypedSymbol('on-table', True, ('b2',)), UntypedSymbol('goal_on', True, ('b2', 'b5')),
                       UntypedSymbol('on', True, ('b1', 'b3')), UntypedSymbol('hand-empty', True, ()),
                       UntypedSymbol('on-table', True, ('b3',))})
        self.assertTrue(UntypedSymbol('done', False, ('b1',)) not in state)


if __name__ == '__main__':
    unittest.main()
