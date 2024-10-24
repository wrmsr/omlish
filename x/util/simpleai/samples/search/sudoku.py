import collections
import copy
import io
import itertools
import string
import time

from ...search import CspProblem
from ...search import backtrack
from ...search import convert_to_binary


variables = ['%s%d' % (i, j) for i in string.ascii_uppercase[:9] for j in range(1, 10)]

domains = collections.OrderedDict((v, list(range(1, 10))) for v in variables)


def const_different(variables, values):
    return values[0] != values[1]  # expect the value of the neighbors to be different


sudoku = """
  3 2 6
9  3 5  1
  18 64
  81 29
7       8
  67 82
  26 95
8  2 3  9
  5 1 3
"""


def parsepuzzle(puzzle):
    sudoku_lines = list(map(lambda s: s.rstrip('\n'), io.StringIO(puzzle).readlines()[1:]))
    domains = {}

    for k, i in enumerate(string.ascii_uppercase[:9]):
        for j in range(1, 10):
            line = sudoku_lines[k]
            if len(line) <= (j - 1):
                continue
            val = line[j - 1]
            if val != ' ':
                var = '%s%d' % (i, j)
                domains[var] = [int(val)]

    return domains


def mkconstraints():
    """
    Make constraint list for binary constraint problem.
    """
    constraints = []

    for j in range(1, 10):
        vars = ['%s%d' % (i, j) for i in string.ascii_uppercase[:9]]
        constraints.extend((c, const_different) for c in itertools.combinations(vars, 2))

    for i in string.ascii_uppercase[:9]:
        vars = ['%s%d' % (i, j) for j in range(1, 10)]
        constraints.extend((c, const_different) for c in itertools.combinations(vars, 2))

    for b0 in ['ABC', 'DEF', 'GHI']:
        for b1 in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
            vars = ['%s%d' % (i, j) for i in b0 for j in b1]
            l = list((c, const_different) for c in itertools.combinations(vars, 2))
            constraints.extend(l)

    return constraints


def mknaryconstraints():

    def alldiff(variables, values):
        return len(values) == len(set(values))  # remove repeated values and count

    constraints = []

    for j in range(1, 10):
        vars_ = ['%s%d' % (i, j) for i in string.ascii_uppercase[:9]]
        constraints.append((vars_, alldiff))

    for i in string.ascii_uppercase[:9]:
        vars_ = ['%s%d' % (i, j) for j in range(1, 10)]
        constraints.append((vars_, alldiff))

    for b0 in ['ABC', 'DEF', 'GHI']:
        for b1 in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
            vars_ = ['%s%d' % (i, j) for i in b0 for j in b1]
            constraints.append((vars_, alldiff))

    return constraints


def display_solution(sol):
    for i in string.ascii_uppercase[:9]:
        print(' '.join([str(sol['%s%d' % (i, j)]) for j in range(1, 10)]))


domains.update(parsepuzzle(sudoku))

# -- Hand made binary constraints --
constraints = mkconstraints()
start = time.time()
domains0 = copy.deepcopy(domains)
my_problem = CspProblem(variables, domains0, constraints)
sol = backtrack(my_problem)
elapsed = time.time() - start
display_solution(sol)
print(
    'Took %d seconds to finish using binary constraints' % elapsed,
)  # because of AC3 should be quick


# -- N-ary constraints made binary using hidden variables --
domains1 = copy.deepcopy(domains)
start = time.time()
variables1, domains1, constraints = convert_to_binary(
    variables, domains1, mknaryconstraints(),
)
my_problem = CspProblem(variables1, domains1, constraints)
sol = backtrack(my_problem)
elapsed = time.time() - start
display_solution(sol)
print('Took %d seconds to finish using binary constraints (hidden variables)' % elapsed)


# -- N-ary constraints --
constraints = mknaryconstraints()
domains3 = copy.deepcopy(domains)
start = time.time()
my_problem = CspProblem(variables, domains3, constraints)
sol = backtrack(my_problem)
elapsed = time.time() - start
display_solution(sol)
print('Took %d seconds to finish using n-ary constraints' % elapsed)
