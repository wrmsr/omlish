"""
TODO:
 - Truth/Conjunctions are not Compounds
 - cut.
 - smt

https://www.metalevel.at/acomip/
https://github.com/photonlines/Python-Prolog-Interpreter
https://curiosity-driven.org/prolog-interpreter
https://github.com/clojure/core.logic
https://github.com/logpy/logpy
https://lab.whitequark.org/notes/2020-04-06/minimizing-logic-expressions/
"""
from collections import defaultdict
import abc
import functools
import typing as ta


Functor = ta.Any
Bindings = ta.Mapping['Variable', 'Term']


class Term(abc.ABC):

    @abc.abstractmethod
    def match_bindings(self, other: 'Term') -> ta.Optional[Bindings]:
        raise NotImplementedError

    @abc.abstractmethod
    def substitute_bindings(self, bindings: Bindings) -> 'Term':
        raise NotImplementedError

    @abc.abstractmethod
    def query(self, database: 'Database') -> ta.Iterable['Term']:
        raise NotImplementedError


class Compound(Term):

    def __init__(
            self,
            functor: Functor,
            arguments: ta.Optional[ta.Iterable['Term']] = None,
    ) -> None:
        super().__init__()

        self._functor = functor
        self._arguments = list(arguments or [])

    @property
    def functor(self) -> Functor:
        return self._functor

    @property
    def arguments(self) -> ta.Sequence['Term']:
        return self._arguments

    def __str__(self) -> str:
        return (
            str(self.functor) if len(self.arguments) == 0 else
            f'{self.functor}({", ".join(str(argument) for argument in self.arguments)})'
        )

    def __repr__(self) -> str:
        return str(self)

    def match_bindings(self, other: Term) -> ta.Optional[Bindings]:
        if isinstance(other, Variable):
            return other.match_bindings(self)

        if isinstance(other, Compound):
            if self._functor != other.functor or len(self._arguments) != len(other.arguments):
                return None

            matched_argument_bindings = [l.match_bindings(r) for l, r in zip(self._arguments, other.arguments)]
            return functools.reduce(Database.merge_bindings, [{}] + matched_argument_bindings)  # type: ignore

        return None

    def substitute_bindings(self, bindings: Bindings) -> Term:
        return Compound(
            self.functor,
            [
                argument.substitute_bindings(bindings)
                for argument in self.arguments
            ],
        )

    def query(self, database: 'Database') -> ta.Iterable[Term]:
        yield from database.query(self)


class Truth(Compound):

    def __init__(self) -> None:
        super().__init__('Truth')

    def substitute_bindings(self, bindings: Bindings) -> Term:
        return self

    def query(self, database: 'Database') -> ta.Iterable[Term]:
        yield self


class Conjunction(Compound):

    def __init__(self, arguments: ta.Iterable['Term']) -> None:
        super().__init__('', arguments)

    def __str__(self) -> str:
        return ', '.join(str(argument) for argument in self.arguments)

    def __repr__(self) -> str:
        return str(self)

    def substitute_bindings(self, bindings: Bindings) -> Term:
        return Conjunction([
            argument.substitute_bindings(bindings)
            for argument in self.arguments
        ])

    def query(self, database: 'Database') -> ta.Iterable[Term]:
        def find_solutions(idx, bindings):
            if idx >= len(self.arguments):
                yield self.substitute_bindings(bindings)

            else:
                arg = self.arguments[idx]
                for item in database.query(arg.substitute_bindings(bindings)):
                    combined = Database.merge_bindings(arg.match_bindings(item), bindings)
                    if combined is not None:
                        yield from find_solutions(idx + 1, combined)

        yield from find_solutions(0, {})


class Variable(Term):

    def __init__(self, name: str) -> None:
        super().__init__()

        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return str(self._name)

    def __repr__(self) -> str:
        return str(self)

    def match_bindings(self, other: Term) -> Bindings:
        bindings = {}
        if self != other:
            bindings[self] = other
        return bindings

    def substitute_bindings(self, bindings: Bindings) -> Term:
        bound_variable_value = bindings.get(self)
        if bound_variable_value:
            return bound_variable_value.substitute_bindings(bindings)
        return self

    def query(self, database: 'Database') -> ta.Iterable[Term]:
        yield from database.query(self)


class Rule:

    def __init__(self, head: Term, tail: Term) -> None:
        super().__init__()

        self._head = head
        self._tail = tail

    @property
    def head(self) -> Term:
        return self._head

    @property
    def tail(self) -> Term:
        return self._tail

    def __str__(self) -> str:
        return str(self._head) + ' :- ' + str(self._tail)

    def __repr__(self) -> str:
        return str(self)


class Database:

    def __init__(self, rules: ta.Iterable[Rule]) -> None:
        super().__init__()

        self._rules = list(rules)

    @property
    def rules(self) -> ta.Sequence[Rule]:
        return self._rules

    def __str__(self) -> str:
        return '.\n'.join(str(rule) for rule in self._rules)

    def __repr__(self) -> str:
        return str(self)

    def query(self, goal: Term) -> ta.Iterable[Term]:
        for index, rule in enumerate(self._rules):
            head_bindings = rule.head.match_bindings(goal)

            if head_bindings is not None:
                head_item = rule.head.substitute_bindings(head_bindings)
                tail_item = rule.tail.substitute_bindings(head_bindings)

                for matching_item in tail_item.query(self):
                    tail_bindings = tail_item.match_bindings(matching_item)
                    if tail_bindings is not None:
                        yield head_item.substitute_bindings(tail_bindings)

    @staticmethod
    def merge_bindings(left: ta.Optional[Bindings], right: ta.Optional[Bindings]) -> ta.Optional[Bindings]:
        if left is None or right is None:
            return None

        merged = {}

        for variable, value in left.items():
            merged[variable] = value

        for variable, value in right.items():
            if variable in merged:
                existing = merged[variable]
                shared = existing.match_bindings(value)

                if shared is not None:
                    for shared_variable, shared_value in shared.items():
                        merged[shared_variable] = shared_value
                else:
                    return None

            else:
                merged[variable] = value

        return merged

    def find_solutions(self, query: Compound) -> ta.Union[bool, ta.Mapping[str, ta.Sequence[Term]], None]:
        matches = list(self.query(query))

        variables_by_name = {arg.name: arg for arg in query.arguments if isinstance(arg, Variable)}
        if not matches:
            return False if not variables_by_name else None
        if not variables_by_name:
            return True

        solutions = defaultdict(list)
        for match in matches:
            matching_bindings = query.match_bindings(match)
            if matching_bindings is not None:
                for variable_name, variable in variables_by_name.items():
                    if variable in matching_bindings:
                        solutions[variable_name].append(matching_bindings[variable])

        return solutions
