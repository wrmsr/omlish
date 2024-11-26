"""
Implement me a very tiny implementation of Warren's Abstract Machine in python.

==

Here's a very tiny implementation of Warren's Abstract Machine (WAM) in Python. This simplified version demonstrates the
core concepts of the WAM, focusing on term representation, unification, and variable bindings.

--

Explanation:

Term Representation:
Variables are represented as REF cells pointing to themselves when unbound.
Constants are represented as CON cells containing their value.
Structures are represented with a STR cell pointing to a FUNCTOR, followed by their arguments.

Unification Process:
The unify method implements a stack-based unification algorithm.
It handles variable bindings, structural unification, and constant matching.
The dereference method ensures variables are properly resolved during unification.

Variable Bindings:
After unification, the values of variables X and Y are retrieved using the get_value method.
If a variable is bound to a constant, its value is returned.
If it's part of a structure, the method recursively retrieves the structure's arguments.

This tiny implementation captures the essence of the WAM's handling of terms and unification, providing a foundational
understanding of how Prolog execution can be modeled in Python.
"""
import dataclasses as dc
import typing as ta


@dc.dataclass(eq=False)
class Ref:
    addr: ta.Any


@dc.dataclass(eq=False)
class Str:
    addr: ta.Any  # Points to FUNCTOR cell


@dc.dataclass(eq=False)
class Functor:
    name: ta.Any
    arity: ta.Any


@dc.dataclass(eq=False)
class Con:
    value: ta.Any


class WAM:
    def __init__(self) -> None:
        super().__init__()
        self.heap = []
        self.registers = {}

    def new_variable(self):
        addr = len(self.heap)
        self.heap.append(Ref(addr))
        return addr

    def new_constant(self, value):
        addr = len(self.heap)
        self.heap.append(Con(value))
        return addr

    def new_structure(self, functor_name, arity, args):
        str_addr = len(self.heap)
        functor_addr = str_addr + 1
        self.heap.append(Str(functor_addr))
        self.heap.append(Functor(functor_name, arity))
        for arg in args:
            self.heap.append(arg)
        return str_addr

    def dereference(self, addr):
        cell = self.heap[addr]
        if isinstance(cell, Ref) and cell.addr != addr:
            return self.dereference(cell.addr)
        else:
            return addr

    def unify(self, addr1, addr2):
        stack = [(addr1, addr2)]

        while stack:
            d1, d2 = stack.pop()

            d1 = self.dereference(d1)
            d2 = self.dereference(d2)

            if d1 == d2:
                continue

            cell1 = self.heap[d1]
            cell2 = self.heap[d2]

            if isinstance(cell1, Ref) and not isinstance(cell2, Ref):
                self.heap[d1] = Ref(d2)

            elif isinstance(cell2, Ref) and not isinstance(cell1, Ref):
                self.heap[d2] = Ref(d1)

            elif isinstance(cell1, Ref) and isinstance(cell2, Ref):
                self.heap[d1] = Ref(d2)

            elif isinstance(cell1, Str) and isinstance(cell2, Str):
                functor1 = self.heap[cell1.addr]
                functor2 = self.heap[cell2.addr]
                if functor1.name == functor2.name and functor1.arity == functor2.arity:
                    for i in range(functor1.arity):
                        arg1_addr = cell1.addr + 1 + i
                        arg2_addr = cell2.addr + 1 + i
                        arg1 = self.heap[arg1_addr]
                        arg2 = self.heap[arg2_addr]
                        stack.append((arg1, arg2))

                else:
                    return False

            elif isinstance(cell1, Con) and isinstance(cell2, Con):
                if cell1.value == cell2.value:
                    continue

                else:
                    return False

            else:
                return False

        return True

    def get_value(self, addr):
        addr = self.dereference(addr)
        cell = self.heap[addr]

        if isinstance(cell, Ref):
            return None  # Unbound variable

        elif isinstance(cell, Con):
            return cell.value

        elif isinstance(cell, Str):
            functor = self.heap[cell.addr]
            args = []
            for i in range(functor.arity):
                arg_addr = cell.addr + 1 + i
                arg_heap_addr = self.heap[arg_addr]
                arg_value = self.get_value(arg_heap_addr)
                args.append(arg_value)

            return (functor.name, args)

        else:
            return None


if __name__ == '__main__':
    # Initialize the WAM
    wam = WAM()

    # Build term t1: f(X, g(Y))
    X_addr = wam.new_variable()
    Y_addr = wam.new_variable()
    g_args = [Y_addr]
    g_addr = wam.new_structure('g', 1, g_args)
    f_args = [X_addr, g_addr]
    t1_addr = wam.new_structure('f', 2, f_args)

    # Build term t2: f(a, g(b))
    a_addr = wam.new_constant('a')
    b_addr = wam.new_constant('b')
    g_b_args = [b_addr]
    g_b_addr = wam.new_structure('g', 1, g_b_args)
    f_ab_args = [a_addr, g_b_addr]
    t2_addr = wam.new_structure('f', 2, f_ab_args)

    # Attempt to unify t1 and t2
    if wam.unify(t1_addr, t2_addr):
        print("Unification succeeded")
        X_value = wam.get_value(X_addr)
        Y_value = wam.get_value(Y_addr)
        print("X =", X_value)
        print("Y =", Y_value)
    else:
        print("Unification failed")
