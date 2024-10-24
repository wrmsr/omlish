import unittest

from ...search.traditional import astar
from ...search.traditional import breadth_first
from ...search.traditional import depth_first
from ...search.traditional import greedy
from ...search.traditional import iterative_limited_depth_first
from ...search.traditional import limited_depth_first
from ...search.traditional import uniform_cost
from ...search.viewers import BaseViewer
from .dummies import DummyGraphProblem
from .dummies import DummyProblem
from .dummies import GOAL


class SampleViewer(BaseViewer):

    def __init__(self, expected_fringes):
        super(SampleViewer, self).__init__()
        self.expected_fringes = expected_fringes

    def event(self, name, *params):
        super(SampleViewer, self).event(name, *params)
        if name == 'new_iteration':
            expected = self.expected_fringes.pop(0)
            current = params[0]
            if not all(
                [
                    cu.state == ex_state and cu.cost == ex_cost
                    for cu, (ex_state, ex_cost) in zip(current, expected)
                ],
            ):
                current = ' '.join(
                    [f'<{x.state}, {x.cost}>' for x in current],
                )
                expected = ' '.join([f'<{x[0]}, {x[1]}>' for x in expected])
                raise Exception(
                    f"""Fringe unexpected: {current}. Expected: {expected}""",
                )


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.problem = DummyProblem()
        self.problem.initial_state = 'i'
        self.graph_problem = DummyGraphProblem(DummyGraphProblem.consistent)

    def test_breadth_first(self):
        result = breadth_first(self.problem)
        self.assertEqual(result.state, GOAL)

    def test_depth_first(self):
        result = depth_first(self.problem)
        self.assertEqual(result.state, GOAL)

    def test_limited_depth_first(self):
        result = limited_depth_first(self.problem, depth_limit=3)
        self.assertEqual(result, None)

        result = limited_depth_first(self.problem, depth_limit=6)
        self.assertEqual(result.state, GOAL)

    def test_iterative_limited_depth_first(self):
        result = iterative_limited_depth_first(self.problem)
        self.assertEqual(result.state, GOAL)

    def test_uniform_cost(self):
        result = uniform_cost(self.problem)
        self.assertEqual(result.state, GOAL)

    def test_greedy(self):
        result = greedy(self.problem)
        self.assertEqual(result.state, GOAL)

    def test_astar(self):
        result = astar(self.problem)
        self.assertEqual(result.state, GOAL)

    def test_astar_graph_execution_with_repeated_states_chooses_better_state(self):
        result = astar(self.graph_problem, graph_search=True)
        self.assertEqual(result.state, self.graph_problem.goal)

    def test_astar_graph_doesnt_repeat_states_in_explore_set(self):
        v = SampleViewer(
            [[('s', 0)], [('l', 26), ('a', 15)], [('a', 15), ('r', 42)], [('r', 42)]],
        )
        self.graph_problem.heuristic_dict = DummyGraphProblem.inconsistent
        result = astar(self.graph_problem, graph_search=True, viewer=v)
        self.assertEqual(result.state, self.graph_problem.goal)

    def test_astar_graph_consistent_heuristic(self):
        v = SampleViewer([[('s', 0)], [('a', 15), ('l', 26)], [('l', 25)], [('r', 41)]])
        self.graph_problem.heuristic_dict = DummyGraphProblem.consistent
        result = astar(self.graph_problem, graph_search=True, viewer=v)
        self.assertEqual(result.state, self.graph_problem.goal)

    def test_astar_graph_inadmissible_heuristic(self):
        v = SampleViewer([[('s', 0)], [('l', 26), ('a', 15)], [('r', 42), ('a', 15)]])
        self.graph_problem.heuristic_dict = DummyGraphProblem.inadmissible
        result = astar(self.graph_problem, graph_search=True, viewer=v)
        self.assertEqual(result.state, self.graph_problem.goal)

    def test_astar_tree_inadmissible_heuristic(self):
        v = SampleViewer(
            [
                [('s', 0)],
                [('l', 26), ('a', 15)],
                [('r', 42), ('a', 15), ('a', 36), ('s', 52)],
            ],
        )
        self.graph_problem.heuristic_dict = DummyGraphProblem.inadmissible
        result = astar(self.graph_problem, graph_search=False, viewer=v)
        self.assertEqual(result.state, self.graph_problem.goal)
