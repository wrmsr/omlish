import enum
import typing as ta

from ... import check
from ... import lang
from .base import CompositeOp
from .errors import AbnfError
from .errors import AbnfUnknownRuleError
from .matches import Match
from .ops import Op
from .ops import RuleRef


with lang.auto_proxy_import(globals()):
    from . import parsing


##


def iter_op_rule_refs(op: Op) -> ta.Iterator[RuleRef]:
    if isinstance(op, RuleRef):
        yield op
    elif isinstance(op, CompositeOp):
        for c in op.children:
            yield from iter_op_rule_refs(c)


##


class Channel(enum.Enum):
    STRUCTURE = enum.auto()
    CONTENT = enum.auto()
    COMMENT = enum.auto()
    SPACE = enum.auto()


class Rule(lang.Final):
    def __init__(
            self,
            name: str,
            op: Op,
            *,
            channel: Channel = Channel.STRUCTURE,
            is_token: bool = False,
    ) -> None:
        super().__init__()

        self._name = check.non_empty_str(name)
        self._op = check.isinstance(op, Op)
        self._channel = channel
        self._is_token = is_token

        self._name_f = name.casefold()

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'{self._name!r}, '
            f'channel={self._channel.name}'
            f'{", is_token=True" if self._is_token else ""})'
        )

    def replace_op(self, op: Op) -> Rule:
        return Rule(
            self._name,
            op,
            channel=self._channel,
            is_token=self._is_token,
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
    def channel(self) -> Channel:
        return self._channel

    @property
    def is_token(self) -> bool:
        return self._is_token


#


class RulesCollection(lang.Final, ta.Collection[Rule]):
    def __init__(self, *rules: Rule | RulesCollection) -> None:
        super().__init__()

        rules_set: set[Rule] = set()
        rules_by_name: dict[str, Rule] = {}
        rules_by_name_f: dict[str, Rule] = {}
        rules_by_op: dict[Op, Rule] = {}

        def add(gr: Rule) -> None:
            check.isinstance(gr, Rule)

            check.not_in(gr, rules_set)
            check.not_in(gr._name, rules_by_name)  # noqa
            check.not_in(gr._name_f, rules_by_name_f)  # noqa
            check.not_in(gr._op, rules_by_op)  # noqa

            rules_set.add(gr)
            rules_by_name[gr._name] = gr  # noqa
            rules_by_name_f[gr._name_f] = gr  # noqa
            rules_by_op[gr._op] = gr  # noqa

        for e in rules:
            if isinstance(e, RulesCollection):
                for c in e:
                    add(c)
            else:
                add(e)

        self._rules_set = rules_set
        self._rules_by_name: ta.Mapping[str, Rule] = rules_by_name
        self._rules_by_name_f: ta.Mapping[str, Rule] = rules_by_name_f
        self._rules_by_op: ta.Mapping[Op, Rule] = rules_by_op

    @property
    def rules_set(self) -> ta.AbstractSet[Rule]:
        return self._rules_set

    @property
    def rules_by_name(self) -> ta.Mapping[str, Rule]:
        return self._rules_by_name

    @property
    def rules_by_name_f(self) -> ta.Mapping[str, Rule]:
        return self._rules_by_name_f

    @property
    def rules_by_op(self) -> ta.Mapping[Op, Rule]:
        return self._rules_by_op

    #

    def __len__(self) -> int:
        return len(self._rules_set)

    def __iter__(self) -> ta.Iterator[Rule]:
        return iter(self._rules_set)

    def __contains__(self, item: Rule) -> bool:  # type: ignore[override]
        return item in self._rules_set

    #

    def rule(self, name: str) -> Rule | None:
        return self._rules_by_name_f.get(name.casefold())


##


class Grammar(lang.Final):
    def __init__(
            self,
            *rules: Rule | RulesCollection,
            root: Rule | str | None = None,
            no_validate: bool = False,
    ) -> None:
        super().__init__()

        if len(rules) == 1 and isinstance(r0 := rules[0], RulesCollection):
            self._rules = r0
        else:
            self._rules = RulesCollection(*rules)

        if not no_validate:
            self._validate_rule_refs()

        if isinstance(root, str):
            rn = root
            try:
                root = self._rules.rules_by_name_f[rn.casefold()]
            except KeyError:
                raise AbnfUnknownRuleError(rn) from None
        self._root = root

    def _validate_rule_refs(self) -> None:
        missing: dict[str, list[str]] = {}
        for r in self._rules.rules_by_name.values():
            for rr in iter_op_rule_refs(r.op):
                if rr.name_f not in self._rules.rules_by_name_f:
                    if r.name not in (l := missing.setdefault(rr.name, [])):
                        l.append(r.name)
        if missing:
            raise AbnfUnknownRuleError(missing)

    @property
    def rules(self) -> RulesCollection:
        return self._rules

    @property
    def root(self) -> Rule | None:
        return self._root

    #

    def rule(self, name: str) -> Rule | None:
        return self._rules.rule(name)

    def replace_rules(self, *rules: Rule) -> Grammar:
        rc = RulesCollection(*rules)
        if rc.rules_set == self._rules.rules_set:
            return self

        return Grammar(
            rc,
            root=self._root.name if self._root is not None else None,
        )

    #

    def resolve_root(self, root: Rule | str | None) -> Rule:
        if root is None:
            if (root := self._root) is None:
                raise AbnfError('No root or default root specified')
        elif isinstance(root, str):
            rn = root
            try:
                root = self._rules.rules_by_name_f[rn.casefold()]
            except KeyError:
                raise AbnfUnknownRuleError(rn) from None
        else:
            root = check.in_(check.isinstance(root, Rule), self._rules)
        return root

    def iter_parse(
            self,
            source: str,
            root: Rule | str | None = None,
            *,
            start: int = 0,
            debug: int = 0,
            **kwargs: ta.Any,
    ) -> ta.Iterator[Match]:
        return parsing._default_compiled(self).iter_parse(  # noqa
            source,
            root,
            start=start,
            debug=debug,
            **kwargs,
        )

    def parse(
            self,
            source: str,
            root: Rule | str | None = None,
            *,
            start: int = 0,
            complete: bool = False,
            debug: int = 0,
            **kwargs: ta.Any,
    ) -> Match | None:
        return parsing._default_compiled(self).parse(  # noqa
            source,
            root,
            start=start,
            complete=complete,
            debug=debug,
            **kwargs,
        )
