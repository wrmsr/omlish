import typing as ta

from omlish import check
from omlish import lang

from .errors import AbnfError
from .errors import AbnfIncompleteParseError
from .matches import Match
from .matches import longest_match
from .ops import Op


with lang.auto_proxy_import(globals()):
    from . import parsing


##


class Rule(lang.Final):
    def __init__(
            self,
            name: str,
            op: Op,
            *,
            insignificant: bool = False,
    ) -> None:
        super().__init__()

        self._name = check.non_empty_str(name)
        self._op = check.isinstance(op, Op)
        self._insignificant = insignificant

        self._name_f = name.casefold()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._name!r})'

    def replace_op(self, op: Op) -> 'Rule':
        return Rule(
            self._name,
            op,
            insignificant=self._insignificant,
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def name_f(self) -> str:
        return self._name_f

    @property
    def op(self) -> Op:
        return self._op

    @property
    def insignificant(self) -> bool:
        return self._insignificant


class Grammar(lang.Final):
    def __init__(
            self,
            *rules: Rule,
            root: Rule | str | None = None,
    ) -> None:
        super().__init__()

        rules_set: set[Rule] = set()
        rules_by_name: dict[str, Rule] = {}
        rules_by_name_f: dict[str, Rule] = {}
        rules_by_op: dict[Op, Rule] = {}
        for gr in rules:
            check.isinstance(gr, Rule)
            check.not_in(gr, rules_set)
            check.not_in(gr._name, rules_by_name)  # noqa
            check.not_in(gr._name_f, rules_by_name_f)  # noqa
            check.not_in(gr._op, rules_by_op)  # noqa
            rules_set.add(gr)
            rules_by_name[gr._name] = gr  # noqa
            rules_by_name_f[gr._name_f] = gr  # noqa
            rules_by_op[gr._op] = gr  # noqa
        self._rules = rules_set
        self._rules_by_name: ta.Mapping[str, Rule] = rules_by_name
        self._rules_by_name_f: ta.Mapping[str, Rule] = rules_by_name_f
        self._rules_by_op: ta.Mapping[Op, Rule] = rules_by_op

        if isinstance(root, str):
            root = rules_by_name_f[root.casefold()]
        self._root = root

    @property
    def root(self) -> Rule | None:
        return self._root

    def rule(self, name: str) -> Rule | None:
        return self._rules_by_name_f.get(name.casefold())

    def iter_parse(
            self,
            source: str,
            root: Rule | str | None = None,
            *,
            start: int = 0,
            debug: int = 0,
            **kwargs: ta.Any,
    ) -> ta.Iterator[Match]:
        if root is None:
            if (root := self._root) is None:
                raise AbnfError('No root or default root specified')
        else:
            if isinstance(root, str):
                root = self._rules_by_name_f[root.casefold()]
            else:
                root = check.in_(check.isinstance(root, Rule), self._rules)

        return parsing._iter_parse(  # noqa
            self,
            source,
            root._op,  # noqa
            start,
            debug=debug,
            **kwargs,
        )

    def parse(
            self,
            source: str,
            root: str | None = None,
            *,
            start: int = 0,
            complete: bool = False,
            debug: int = 0,
            **kwargs: ta.Any,
    ) -> Match | None:
        if (match := longest_match(self.iter_parse(
                source,
                root,
                start=start,
                debug=debug,
                **kwargs,
        ))) is None:
            return None

        if complete and (match.start, match.end) != (start, len(source)):
            raise AbnfIncompleteParseError

        return match
