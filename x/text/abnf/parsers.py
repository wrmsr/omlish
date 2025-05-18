import abc
import collections
import itertools
import pathlib
import typing as ta
import weakref

from omlish import check

from .errors import GrammarError
from .errors import ParseError
from .matches import Match
from .matches import Matches
from .matches import MatchSet
from .matches import next_longest_match
from .matches import sorted_by_longest_match
from .nodes import LiteralNode
from .nodes import Node


##


class Parser(abc.ABC):
    # def parse(
    #    self, source: str, start: int
    # ) -> tuple[Nodes, int]:  # pragma: no cover
    #   ...
    @abc.abstractmethod
    def lparse(self, source: str, start: int) -> Matches:
        raise NotImplementedError


##


ParseCacheKey: ta.TypeAlias = tuple[str, int]
ParseCacheValue: ta.TypeAlias = ta.Union[MatchSet, 'ParseError']


class ParseCache(ta.MutableMapping[ParseCacheKey, ParseCacheValue]):
    max_cache_size: int | None = None
    objects: weakref.WeakSet['ParseCache'] = weakref.WeakSet()

    def __new__(cls, max_size: int | None = None) -> ta.Any:  # noqa
        obj = super().__new__(cls)
        cls.objects.add(obj)
        return obj

    def __init__(self, max_size: int | None = None) -> None:
        super().__init__()

        self.dict: collections.OrderedDict[ParseCacheKey, MatchSet | ParseError] = collections.OrderedDict()

        if max_size is None:
            max_size = self.max_cache_size
        if max_size and max_size < 0:
            msg = 'max size must be non-negative.'
            raise ValueError(msg)
        self.max_size = max_size

        self.hits = 0
        self.misses = 0

    def __getitem__(self, key: ParseCacheKey) -> ParseCacheValue:
        try:
            value = self.dict[key]
        except KeyError:
            self.misses = self.misses + 1
            raise
        else:
            self.hits = self.hits + 1
            self.dict.move_to_end(key)
            return value

    def __setitem__(self, key: ParseCacheKey, value: ParseCacheValue) -> None:
        # here we want to expel least recently used entries, defined to the first entries in the order.
        self.dict[key] = value
        if self.max_size and len(self.dict) > self.max_size:
            self.dict.popitem(last=False)

    def __delitem__(self, key: ParseCacheKey) -> None:
        del self.dict[key]

    def __iter__(self) -> ta.Iterator[ParseCacheKey]:
        return self.dict.__iter__()

    def __len__(self) -> int:
        return len(self.dict)

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, /, o: object) -> bool:
        return hash(self) == hash(o)

    def __str__(self) -> str:
        return (
                f'{self.__class__.__name__}('
                f'max_size={self.max_size}, '
                f'size={len(self)}, '
                f'misses={self.misses}, '
                f'hits={self.hits})'
        )

    @classmethod
    def clear_caches(cls) -> None:
        for obj in cls.objects:
            obj.dict = collections.OrderedDict()
            obj.hits = 0
            obj.misses = 0

    @classmethod
    def list(cls) -> ta.Iterator:
        yield from cls.objects


##


class Alternation(Parser):
    """
    Implements the ABNF alternation operator. -- Alternation(parser1, parser2, ...) returns a parser that invokes
    parser1, parser2, ... in turn and returns the result of the first successful parse..
    """

    str_template = 'Alternation(%s)'

    def __init__(self, *parsers: Parser, first_match: bool = False) -> None:
        super().__init__()

        self.parsers = list(parsers)
        self.first_match = first_match

    def lparse(self, source: str, start: int) -> Matches:
        match_found = False
        for parser in self.parsers:
            try:
                # note that parser,lparse could return an empty list, say from
                # something like *"a" .
                for item in parser.lparse(source, start):
                    match_found = True
                    yield (item)
            except ParseError:
                continue
            if self.first_match:
                return
        if not match_found:
            raise ParseError(self, start)

    def __str__(self):
        return self.str_template % ', '.join(map(str, self.parsers))


class Concatenation(Parser):
    """
    Implements the ABNF concatention operation. Concatention(parser1, parser2, ...) returns a parser that invokes
    parser1, parser2, ... in turn and returns a list of Nodes if every parser succeeds.
    """

    str_template = 'Concatenation(%s)'

    def __init__(self, *parsers: Parser) -> None:
        super().__init__()

        self.parsers = parsers

    def lparse(self, source: str, start: int) -> Matches:
        match_list: list[Match] = [Match([], start)]

        for parser in self.parsers:
            current_match_list: list[Match] = []

            for match in match_list:
                try:  # noqa: SIM105
                    current_match_list.extend(
                        [
                            Match(match.nodes + m.nodes, m.start)
                            for m in parser.lparse(source, match.start)
                        ],
                    )
                except ParseError:  # noqa: PERF203
                    pass

            if current_match_list:
                match_list = current_match_list
            else:
                raise ParseError(self, start)

        yield from sorted_by_longest_match(match_list)

    def __str__(self):
        return self.str_template % ', '.join(map(str, self.parsers))


class Repeat:
    """Implements the ABNF Repeat operator for Repetition."""

    def __init__(self, min: int = 0, max: int | None = None) -> None:  # noqa
        super().__init__()

        self.min = min
        self.max = max

    def __str__(self):
        _min = self.min
        _max = self.max if self.max is not None else 'None'
        return f'Repeat({_min}, {_max})'


class Repetition(Parser):
    """Implements the ABNF Repetition operation."""

    def __init__(self, repeat: Repeat, element: Parser) -> None:
        super().__init__()

        self.repeat = repeat
        self.element = element
        self.lparse_cache = ParseCache()

    def lparse(self, source: str, start: int) -> Matches:
        cache_key = (source, start)
        try:
            cached_matchset = self.lparse_cache[cache_key]
        except KeyError:
            pass
        else:
            if isinstance(cached_matchset, ParseError):
                raise cached_matchset
            yield from next_longest_match(cached_matchset)
            return

        if self.repeat.min == 0:
            match_set: MatchSet = {Match([], start)}
        else:
            concat_parser = Concatenation(*([self.element] * self.repeat.min))
            try:
                # if this raises a ParseError, then the minimum match was not reached.
                match_set = set(concat_parser.lparse(source, start))
            except ParseError as exc:
                self.lparse_cache[cache_key] = exc
                raise

        last_match_set = set(match_set)
        match_count = self.repeat.min

        while True:
            if self.repeat.max is not None and match_count == self.repeat.max:
                break

            new_match_set: MatchSet = set()
            for match in last_match_set:
                g = self.element.lparse(source, match.start)
                try:  # noqa: SIM105
                    new_match_set.update(
                        [Match(match.nodes + m.nodes, m.start) for m in g],
                    )
                except ParseError:
                    pass

            if not new_match_set <= match_set:
                match_count = match_count + 1
                match_set = match_set | new_match_set
                last_match_set = new_match_set
            else:
                break

        self.lparse_cache[cache_key] = match_set
        yield from next_longest_match(match_set)

    def __str__(self):
        return f'Repetition({self.repeat}, {self.element})'


class Option(Parser):
    """Implements the ABNF Option operation."""

    str_template = 'Option(%s)'

    def __init__(self, alternation: Parser) -> None:
        super().__init__()

        self.alternation = alternation
        self.parser = Repetition(Repeat(0, 1), alternation)

    def lparse(self, source: str, start: int) -> Matches:
        return self.parser.lparse(source, start)

    def __str__(self):
        return self.str_template % str(self.alternation)


class Literal(Parser):
    """Represents a terminal literal value."""

    def __init__(
        self,
        value: str | tuple[str, str],
        case_sensitive: bool = False,
    ) -> None:
        """
        value is either a string to be matched, or a two-element tuple representing an
        inclusive range; e.g. ('a', 'z') matches all letters a-z.
        """

        super().__init__()

        if not (
            isinstance(value, str)
            or (
                isinstance(value, tuple)
                and len(value) == 2
                and isinstance(value[0], str)
                and isinstance(value[1], str)
            )
        ):
            msg = 'value argument must be a string or a 2-tuple of strings.'  # type: ignore[unreachable]
            raise TypeError(msg)

        self.value = value
        self.case_sensitive = case_sensitive
        self.pattern = (
            value if isinstance(value, tuple) or case_sensitive else value.casefold()
        )

    def lparse(self, source: str, start: int) -> Matches:
        if isinstance(self.value, tuple):
            return self._lparse_range(source, start)
        else:
            return self._lparse_value(source, start)

    def _lparse_range(self, source: str, start: int) -> Matches:
        """Parse source when self.value represents a range."""

        # ranges are always case-sensitive
        try:
            src = source[start]
            if self.value[0] <= src <= self.value[1]:
                yield Match([ta.cast('Node', LiteralNode(src, start, 1))], start + 1)
            else:
                raise ParseError(self, start)
        except IndexError as e:
            raise ParseError(self, start) from e

    def _lparse_value(self, source: str, start: int) -> Matches:
        """Parse source when self.value represents a literal."""

        # we check position to ensure that the case pattern = '' and start >= len(source)
        # is handled correctly.
        if start < len(source):
            src = source[start : start + len(self.value)]
            match = src if self.case_sensitive else src.casefold()
            if match == self.pattern:
                yield Match(
                    [ta.cast('Node', LiteralNode(src, start, len(src)))],
                    start + len(src),
                )
            else:
                raise ParseError(self, start)
        else:
            raise ParseError(self, start)

    def __str__(self):
        # str(self.value) handles the case value == tuple.
        non_printable_chars = set(map(chr, range(0x20)))
        value = tuple(
            rf'\x{ord(x):02x}' if x in non_printable_chars else x for x in self.value
        )

        return (
            f'Literal({value})'
            if isinstance(self.value, tuple)
            else "Literal('%s'%s)"  # noqa: UP031
            % (''.join(value), ', case_sensitive' if self.case_sensitive else '')
        )


class Prose(Parser):
    def lparse(self, source: str, start: int) -> Matches:
        raise ParseError(self, start)


class Rule(Parser):
    """
    A parser generated from an ABNF rule.

    To create a Rule object, use Rule.create.

    rule = Rule.create('URI = scheme ":" hier-part [ "?" query ] [ "#" fragment ]')
    """

    GRAMMAR: ta.ClassVar[list[str] | str] = []

    _obj_map: ta.ClassVar[dict[tuple[type['Rule'], str], 'Rule']] = {}

    def __new__(cls, name: str, definition: Parser | None = None) -> ta.Any:  # noqa
        """Overrides super().__new__ to implement a symbol table via object caching."""

        rule = cls.get(name)
        if rule is None:
            rule = super().__new__(cls)
            obj_key = (cls, name.casefold())
            cls._obj_map[obj_key] = rule
        return check.not_none(rule)

    def __init__(self, name: str, definition: Parser | None = None) -> None:
        super().__init__()

        try:
            _ = self.name  # type: ignore[has-type]
        except AttributeError:
            self.name = name
        try:
            _ = self.exclude
        except AttributeError:
            self.exclude: Rule | None = None

        if definition is not None:
            # when defined-as = '=/', we'll need to overwrite existing definition.
            self.definition = definition

    @property
    def first_match_alternation(self) -> bool:
        try:
            definition = self.definition
        except AttributeError:
            return False
        else:
            return isinstance(definition, Alternation) and definition.first_match

    @first_match_alternation.setter
    def first_match_alternation(self, value: bool):
        try:
            definition = self.definition
        except AttributeError as exc:
            msg = f'Undefined rule "{self.name}"'
            raise GrammarError(msg) from exc
        else:
            if isinstance(definition, Alternation):
                definition.first_match = value
            else:
                # skip. Or should some exception be raised?
                pass

    def exclude_rule(self, rule: 'Rule') -> None:
        """
        Exclude values which match rule. For example, suppose we have the following grammar.
        foo = %x66.6f.6f
        keyword = foo
        identifier = ALPHA *(ALPHA / DIGIT )

        We don't want to allow a keyword to be an identifier. To do this,
        Rule('identifier').exclude_rule(Rule('keyword'))

        Then attempting to use "foo" as an identifier would result in a ParseError.
        """

        self.exclude = rule

    def lparse(self, source: str, start: int) -> Matches:
        def exclude(match: Match) -> bool:
            if self.exclude is None:
                return False

            try:
                self.exclude.parse_all(''.join(item.value for item in match.nodes))
            except ParseError:
                return False
            else:
                return True

        try:
            g = self.definition.lparse(source, start)
        except AttributeError as exc:
            msg = f'Undefined rule "{self.name}"'
            raise GrammarError(msg) from exc

        matches = set(itertools.filterfalse(exclude, g))
        if matches:
            yield from [
                Match([Node(self.name, *match.nodes)], match.start) for match in matches
            ]
        else:
            raise ParseError(self, start) from None

    def parse(self, source: str, start: int) -> tuple['Node', int]:
        g = self.lparse(source, start)
        matches = set(g)
        check.not_empty(matches)
        # we return the longest match. It is possible that there is more than one
        # match of maximal length. Call lparse to see all amatches
        longest_match = next(next_longest_match(matches))
        return (longest_match.nodes[0], longest_match.start)

    def parse_all(self, source: str) -> 'Node':
        """
        Parses the source from beginning to end. If not all of the source is consumed, a ParseError is raised.
        """

        node, start = self.parse(source, 0)
        if start < len(source):
            raise ParseError(self, start)
        return node

    def __str__(self):
        return f"{self.__class__.__name__}('{self.name}')"

    @classmethod
    def create(cls, rule_source: str, start: int = 0) -> ta.Self:
        """
        Creates a Rule object from ABNF source. A terminating CRLF will be appended to rule_source if needed to satisfy
        the ABNF grammar rule for "rule".
        """

        from .core import GrammarNodeVisitor
        from .core import GrammarRule

        if rule_source[-2:] != '\r\n':
            rule_source = rule_source + '\r\n'
        grule = GrammarRule('rule')
        try:
            parse_tree, start = grule.parse(rule_source, start)
        except ParseError:
            raise
        visitor = GrammarNodeVisitor(cls)
        rule = visitor.visit(parse_tree)
        return rule

    @classmethod
    def load_grammar(cls, grammar: str, strict: bool = True) -> None:
        """
        Loads grammar and attempts to parse it as a rulelist. If successful, cls is populated with the rules in the
        rulelist. When strict = True, line endings following rules are normalized to CRLF to satisfy the definition of
        'rulelist. If strict is set to False, the grammar is parsed as is.
        """

        check.isinstance(grammar, str)

        if strict:
            # process to ensure that line endings are correct.
            cr = '\r'
            lf = '\n'
            crlf = cr + lf
            src = grammar.rstrip().replace(cr, '').replace(lf, crlf) + crlf
        else:
            src = grammar

        from .core import GrammarNodeVisitor
        from .core import GrammarRule

        node = GrammarRule('rulelist').parse_all(src)
        visitor = GrammarNodeVisitor(rule_cls=cls)
        visitor.visit(node)

    @classmethod
    def from_file(cls, path: str | pathlib.Path) -> None:
        """
        Loads the contents of path and attempts to parse it as a rulelist. If successful, cls is populated with the
        rules in the rulelist.
        """

        crlf = '\r\n'
        with (
            open(path, newline=crlf, encoding='ascii')
            if isinstance(path, str)
            else path.open('r', newline=crlf, encoding='ascii')
        ) as f:
            src = f.read()
        cls.load_grammar(src)

    @classmethod
    def get(
        cls, name: str, default: ta.Self | None = None,
    ) -> ta.Optional['Rule']:
        """
        Retrieves Rule by name. If a Rule object matching name is found, it is returned. Otherwise default is returned,
        and no Rule object is created, as would be the case when invoking Rule(name). Note that
        """

        _name = name.casefold()
        return cls._obj_map.get((cls, _name), cls._obj_map.get((Rule, _name), default))

    @classmethod
    def rules(cls):
        """
        Returns a list of all rules created.

        :returns: list
        """

        return [v for k, v in cls._obj_map.items() if k[0] is cls]
