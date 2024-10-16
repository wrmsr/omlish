import copy
import time

from ...search import CspProblem
from ...search import backtrack
from ...search import convert_to_binary


variables = ('X1', 'X2', 'X3', 'X4', 'X5', 'X6')

domains = dict((v, [False, True]) for v in variables)

constraints = [
    (('X1', 'X2', 'X6'), lambda v, values: values[0] or values[1] or values[2]),
    (('X1', 'X3', 'X4'), lambda v, values: not values[0] or values[1] or values[2]),
    (('X4', 'X5', 'X6'), lambda v, values: not values[0] or not values[1] or values[2]),
    (('X2', 'X5', 'X6'), lambda v, values: values[0] or values[1] or not values[2]),
]

original_constraints = copy.deepcopy(constraints)
original_domains = copy.deepcopy(domains)

start = time.time()
problem = CspProblem(variables, original_domains, original_constraints)
result = backtrack(problem)
elapsed = time.time() - start
print(result)
print('Took %d seconds to finish using n-ary constraints' % elapsed)


start = time.time()
variables, domains, constraints = convert_to_binary(variables, domains, constraints)
problem = CspProblem(variables, domains, constraints)
result = backtrack(problem)
elapsed = time.time() - start
print(result)
print('Took %d seconds to finish using binary constraints' % elapsed)
