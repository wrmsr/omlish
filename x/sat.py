"""
https://github.com/toanphan19/tiny-sat/blob/dae82b5e993356bb80ee62ed46dffe6baa4f65f5/tinysat-python/solvers/dpll_solver.py

https://github.com/eliben/code-for-blog/tree/main/2007/sudoku_sat

https://github.com/eliben/code-for-blog/blob/main/2007/sudoku_sat/sat_solver.rb
https://github.com/eliben/code-for-blog/blob/main/2007/sudoku_sat/test_sat_solver.rb
"""
# MIT License
#
# Copyright (c) 2020 Toan N. Phan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import copy
import enum
import random
import sys
import time
import typing as ta


class DPLLSolver:
    """
    A SAT solver using DPLL algorithm.

    Parameters:
    `var_choice`: {"input_order", "most_appearance"}, optional.
        Default is "input_order".
    `solve_all`: boolean, optional. Default is False, which means the solver will terminate after having found the first
        solution.
    """

    def __init__(self, var_choice="input_order", solve_all=False):
        # TODO: Implement the algorithm to solve all possible assignment.

        self.instance = None
        self.assignment = []  # assignment[v]: {True, False, None}
        self.propagator = None
        self.unassigned_vars = []
        self.satisfy_assignment = []  # list of satisfying assignment found.

        self.var_choice = var_choice

    def solve(self, instance):
        self.instance = instance
        self.assignment = [None for _ in range(instance.var_count)]
        self.propagator = Propagator(instance)
        self.unassigned_vars = self.setup_branch_order(instance)

        # print(f"\nBranch order: {[x+1 for x in self.unassigned_vars]}")

        self.dpll(0)
        return len(self.get_assignments()) > 0

    def dpll(self, level):
        """
        `level`: the current decision level. Used for backtracking.
        """

        if level == self.instance.var_count:
            self.save_assignment()
            # print(f"Successful assignment:\n {self.assignment}")

            return True

        # Pick a variable & try assigning value to it:
        variable = self.pick_branching_var()
        values = self.pick_assignment_order()

        self.assign(variable, values[0])
        if self.propagator.propagate(var_to_lit(variable, values[0]), self.assignment):
            if self.dpll(level + 1):
                return True

        self.assign(variable, values[1])
        if self.propagator.propagate(var_to_lit(variable, values[1]), self.assignment):
            if self.dpll(level + 1):
                return True

        # Roll back to backtrack:
        self.unassign(variable)
        return False

    def setup_branch_order(self, instance):
        if self.var_choice == "most_appearance":
            all_literals = [l for clause in instance.clauses for l in clause]

            # Sort variables according to their decreasing number of appearances
            order = copy.copy(instance.variables)
            order.sort(
                key=lambda v: all_literals.count(var_to_lit(v, True))
                + all_literals.count(var_to_lit(v, False)),
                reverse=True,
            )
        else:
            order = copy.copy(instance.variables)

        return order

    def pick_branching_var(self):
        """Choose the unassigned variable according to self.var_choice"""

        var = self.unassigned_vars[0]
        return var

    def pick_assignment_order(self):
        """Randomly choose the order of value to make an assignment"""

        if random.random() >= 0.5:
            return (True, False)
        return (False, True)

    def assign(self, variable, value):
        self.assignment[variable] = value
        if variable in self.unassigned_vars:
            self.unassigned_vars.remove(variable)

    def unassign(self, variable):
        self.assignment[variable] = None
        self.unassigned_vars.append(variable)

    def save_assignment(self):
        self.satisfy_assignment.append(copy.copy(self.assignment))

    def get_assignments(self):
        """Return the list of satisfying assignments."""

        return self.satisfy_assignment


##


def __encode_literal(x):
    return (x - 1) * 2 if x > 0 else (-x - 1) * 2 + 1


def __parse_clause(line):
    """Converting a clause to an array of literals."""

    literals = [int(x) for x in line.split()]
    if literals[-1] != 0:
        raise Exception("Parsing error: All clauses must end with 0.")

    literals = [__encode_literal(x) for x in literals[:-1]]
    return literals


def parse_program(program):
    """Parse a program (of type string) and return an Instance"""

    # TODO: Check number of vars and clauses to see if they match

    lines = program.strip().split("\n")

    # Ignore comments at the beginning of the file:
    start_i = 0
    while lines[start_i][0] != "p":
        start_i += 1
    lines = lines[start_i:]

    var_count, clause_count = lines[0].split()[2:4]
    var_count, clause_count = int(var_count), int(clause_count)

    variables = list(range(var_count))
    clauses = []
    for i in range(1, clause_count + 1):
        clauses.append(__parse_clause(lines[i]))

    return Instance(variables, clauses)


def decode_assignment(assignment):
    result = [i + 1 if assignment[i] else -(i + 1) for i in range(len(assignment))]
    return " ".join([str(x) for x in result])


##


def lit_to_var(literal):
    return (literal // 2, literal % 2 == 0)


def var_to_lit(variable, value):
    """
    variable: int
    value: boolean
    """

    return variable * 2 + int(value)


##


class Instance:
    def __init__(self, variables, clauses):
        """
        self.variables: [1, 2, 3, 4]
        self.clauses: [(0, 2, 5), (3, 4, 5)]
        """

        self.var_count = len(variables)
        self.clause_count = len(clauses)
        self.variables = variables
        self.clauses = clauses

    def __str__(self):
        text = f"Variables: {self.var_count}\n{self.variables}\n"
        text += f"Clauses: {self.clause_count}\n{self.clauses}\n"
        return text


##


class Propagator:
    def __init__(self, instance):
        self.instance = instance
        self.watchlist = self.setup_watchlist(instance)

    def setup_watchlist(self, instance):
        watchlist = [[] for x in range(2 * instance.var_count)]
        for idx, clause in enumerate(instance.clauses):
            watchlist[clause[0]].append(idx)

        return watchlist

    def propagate(self, false_literal, assignment):
        """
        At least a literal in a clause must be true to satisfy a clause. When a literal is assigned false, we make all
        the clauses watching that literal to watch another literal. If all other literal are false => clause unsatisfied

        Return: False if cannot update watchlist, which means the formula is unsatisfiable; True otherwise.
        """

        watchlist = self.watchlist
        while len(watchlist[false_literal]) > 0:
            clause_id = watchlist[false_literal][0]
            found_another = False
            for literal in self.instance.clauses[clause_id]:
                if literal == false_literal:
                    continue
                variable, is_positive = lit_to_var(literal)

                if assignment[variable] is None or assignment[variable] == is_positive:
                    found_another = True
                    watchlist[literal].append(clause_id)
                    watchlist[false_literal].remove(clause_id)
                    break

            if not found_another:
                return False

        return True


##


class Satisfiability(enum.Enum):
    SAT = "SATISFIABLE"
    UNSAT = "UNSATISFIABLE"
    # UNKNOWN = 'UNKNOWN'


def run_solver(program):
    instance = parse_program(program)
    solver = DPLLSolver("input_order")
    is_sat = solver.solve(instance)

    if is_sat:
        assignments = solver.get_assignments()
        assignments = [decode_assignment(a) for a in assignments]
        return Satisfiability.SAT, assignments
    else:
        return Satisfiability.UNSAT, None


##


SIMPLE = """
c  simple_v3_c2.cnf
c
p cnf 3 3
1 -3 0
2 3 -1 0
-1 0
"""


SIMPLE2 = """
p cnf 17 10
-1 -3 4 0
-1 -5 6 0
-8 -7 9 0
-8 -5 10 0
-1 -11 -2 0
-8 -13 -10 0
-14 15 0
-11 16 0
-12 17 0
-7 -15 0
"""


SIMPLE_UNSAT = """
p cnf 5 13
1 2 3 0
1 -2 3 0
2 3 4 0
-1 3 5 0
1 4 5 0
2 -4 -5 0
3 4 5 0
3 -4 -5 0
-2 -3 -4 0
1 2 3 4 5 0
-1 -2 -3 -4 -5 0
-3 0
-1 -2 0
"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # print("There are not enough arguments!")
        # print("Expected: python tinysat.py <input file>")
        # sys.exit()

        program = SIMPLE
        # program = SIMPLE2
        # program = SIMPLE_UNSAT

    else:
        with open(sys.argv[1]) as f:
            program = f.read()

    start_time = time.time()
    result, assignments = run_solver(program)
    elapsed_time = time.time() - start_time

    print()
    if result == Satisfiability.UNSAT:
        print("UNSAT")
    else:
        print("SAT")
        for a in assignments:
            print(a)

    print(f"Time elapse: {elapsed_time * 1000:.2f}ms")
