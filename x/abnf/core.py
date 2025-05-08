import typing as ta

from omlish import check
from omlish import lang

from .errors import ParseError
from .nodes import Node
from .nodes import NodeVisitor
from .parsers import Alternation
from .parsers import Concatenation
from .parsers import Literal
from .parsers import Option
from .parsers import Parser
from .parsers import Prose
from .parsers import Repeat
from .parsers import Repetition
from .parsers import Rule


##
# Bootstrapping.
#
# To get parsing for parser generation started, the ABNF grammar from RFC 5234 and RFC 7405, plus the core rules from
# RFC 5234, are defined ab initio.


BOOTSTRAP_RULES: list[tuple[str, Parser]] = [

    ('ALPHA', Alternation(
        Literal(('\x41', '\x5a')),
        Literal(('\x61', '\x7a')),
    )),

    ('BIT', Alternation(
        Literal('0'),
        Literal('1'),
    )),

    ('CHAR', Literal(('\x01', '\x7f'))),

    ('CTL', Alternation(
        Literal(('\x00', '\x1f')),
        Literal('\x7f', case_sensitive=True),
    )),

    ('CR', Literal('\x0d', case_sensitive=True)),

    ('CRLF', Concatenation(
        Rule('CR'),
        Rule('LF'),
    )),

    ('DIGIT', Literal(('\x30', '\x39'))),

    ('DQUOTE', Literal('\x22', case_sensitive=True)),

    ('HEXDIG', Alternation(
        Rule('DIGIT'),
        Literal('A'),
        Literal('B'),
        Literal('C'),
        Literal('D'),
        Literal('E'),
        Literal('F'),
    )),

    ('HTAB', Literal('\x09', case_sensitive=True)),

    ('LF', Literal('\x0a', case_sensitive=True)),

    ('LWSP', Repetition(
        Repeat(),
        Alternation(
            Rule('WSP'),
            Concatenation(
                Rule('CRLF'),
                Rule('WSP'),
            ),
        ),
    )),

    ('OCTET', Literal(('\x00', '\xff'))),

    ('SP', Literal('\x20', case_sensitive=True)),

    ('VCHAR', Literal(('\x21', '\x7e'))),

    ('WSP', Alternation(
        Rule('SP'),
        Rule('HTAB'),
    )),

]


@lang.static_init
def _init_bootstrap_rules() -> None:
    for rule_def in BOOTSTRAP_RULES:
        Rule(rule_def[0], rule_def[1])


#


class GrammarRule(Rule):
    """Rules defining ABNF in ABNF."""


BOOTSTRAP_GRAMMAR_RULES: ta.Sequence[tuple[str, Parser]] = [

    ('rulelist', Repetition(
        Repeat(1),
        Alternation(
            GrammarRule('rule'),
            Concatenation(
                Repetition(
                    Repeat(),
                    GrammarRule('c-wsp'),
                ),
                GrammarRule('c-nl'),
            ),
        ),
    )),

    ('rule', Concatenation(
        GrammarRule('rulename'),
        GrammarRule('defined-as'),
        GrammarRule('elements'),
        GrammarRule('c-nl'),
    )),

    ('rulename', Concatenation(
        Rule('ALPHA'),
        Repetition(
            Repeat(),
            Alternation(
                Rule('ALPHA'),
                Rule('DIGIT'),
                Literal('-'),
            ),
        ),
    )),

    ('defined-as', Concatenation(
        Repetition(
            Repeat(),
            GrammarRule('c-wsp'),
        ),
        Alternation(
            Literal('=/'),
            Literal('='),
        ),
        Repetition(
            Repeat(),
            GrammarRule('c-wsp'),
        ),
    )),

    ('elements', Concatenation(
        GrammarRule('alternation'),
        Repetition(
            Repeat(),
            GrammarRule('c-wsp'),
        ),
    )),

    ('c-wsp', Alternation(
        Rule('WSP'),
        Concatenation(
            GrammarRule('c-nl'),
            Rule('WSP'),
        ),
    )),

    ('c-nl', Alternation(
        GrammarRule('comment'),
        Rule('CRLF'),
    )),

    ('comment', Concatenation(
        Literal(';'),
        Repetition(
            Repeat(),
            Alternation(
                Rule('WSP'),
                Rule('VCHAR'),
            )),
        Rule('CRLF'),
    )),

    ('alternation', Concatenation(
        GrammarRule('concatenation'),
        Repetition(
            Repeat(),
            Concatenation(
                Repetition(
                    Repeat(),
                    GrammarRule('c-wsp'),
                ),
                Literal('/'),
                Repetition(
                    Repeat(),
                    GrammarRule('c-wsp'),
                ),
                GrammarRule('concatenation'),
            ),
        ),
    )),

    ('concatenation', Concatenation(
        GrammarRule('repetition'),
        Repetition(
            Repeat(),
            Concatenation(
                Repetition(
                    Repeat(1),
                    GrammarRule('c-wsp'),
                ),
                GrammarRule('repetition'),
            ),
        ),
    )),

    ('repetition', Concatenation(
        Option(
            GrammarRule('repeat'),
        ),
        GrammarRule('element'),
    )),

    ('repeat', Alternation(
        Concatenation(
            Repetition(
                Repeat(0, None),
                Rule('DIGIT'),
            ),
            Literal('*'),
            Repetition(
                Repeat(0, None),
                Rule('DIGIT'),
            ),
        ),
        Repetition(
            Repeat(1, None),
            Rule('DIGIT'),
        ),
    )),

    ('element', Alternation(
        GrammarRule('rulename'),
        GrammarRule('group'),
        GrammarRule('option'),
        GrammarRule('char-val'),
        GrammarRule('num-val'),
        GrammarRule('prose-val'),
    )),

    ('group', Concatenation(
        Literal('('),
        Repetition(
            Repeat(),
            GrammarRule('c-wsp'),
        ),
        GrammarRule('alternation'),
        Repetition(
            Repeat(),
            GrammarRule('c-wsp'),
        ),
        Literal(')'),
    )),

    ('option', Concatenation(
        Literal('['),
        Repetition(
            Repeat(),
            GrammarRule('c-wsp'),
        ),
        GrammarRule('alternation'),
        Repetition(
            Repeat(),
            GrammarRule('c-wsp'),
        ),
        Literal(']'),
    )),

    ('num-val', Concatenation(
        Literal('%'),
        Alternation(
            GrammarRule('bin-val'),
            GrammarRule('dec-val'),
            GrammarRule('hex-val'),
        ),
    )),

    ('bin-val', Concatenation(
        Literal('b'),
        Concatenation(
            Repetition(
                Repeat(1),
                Rule('BIT'),
            ),
            Option(
                Alternation(
                    Repetition(
                        Repeat(1),
                        Concatenation(
                            Literal('.'),
                            Repetition(
                                Repeat(1),
                                Rule('BIT'),
                            ),
                        ),
                    ),
                    Concatenation(
                        Literal('-'),
                        Repetition(
                            Repeat(1),
                            Rule('BIT'),
                        ),
                    ),
                ),
            ),
        ),
    )),

    ('dec-val', Concatenation(
        Literal('d'),
        Concatenation(
            Repetition(
                Repeat(1),
                Rule('DIGIT'),
            ),
            Option(
                Alternation(
                    Repetition(
                        Repeat(1),
                        Concatenation(
                            Literal('.'),
                            Repetition(
                                Repeat(1),
                                Rule('DIGIT'),
                            ),
                        ),
                    ),
                    Concatenation(
                        Literal('-'),
                        Repetition(
                            Repeat(1),
                            Rule('DIGIT'),
                        ),
                    ),
                ),
            ),
        ),
    )),

    ('hex-val', Concatenation(
        Literal('x'),
        Concatenation(
            Repetition(
                Repeat(1),
                Rule('HEXDIG'),
            ),
            Option(
                Alternation(
                    Repetition(
                        Repeat(1),
                        Concatenation(
                            Literal('.'),
                            Repetition(
                                Repeat(1),
                                Rule('HEXDIG'),
                            ),
                        ),
                    ),
                    Concatenation(
                        Literal('-'),
                        Repetition(
                            Repeat(1),
                            Rule('HEXDIG'),
                        ),
                    ),
                ),
            ),
        ),
    )),

    ('prose-val', Concatenation(
        Literal('<'),
        Repetition(
            Repeat(),
            Alternation(
                Literal(('\x20', '\x3d')),
                Literal(('\x3f', '\x7e')),
            ),
        ),
        Literal('>'),
    )),

    # definitions from RFC 7405
    ('char-val', Alternation(
        GrammarRule('case-insensitive-string'),
        GrammarRule('case-sensitive-string'),
    )),

    ('case-insensitive-string', Concatenation(
        Option(
            Literal('%i'),
        ),
        GrammarRule('quoted-string'),
    )),

    ('case-sensitive-string', Concatenation(
        Literal('%s'),
        GrammarRule('quoted-string'),
    )),

    ('quoted-string', Concatenation(
        Rule('DQUOTE'),
        Repetition(
            Repeat(),
            Alternation(
                Literal(('\x20', '\x21')),
                Literal(('\x23', '\x7e')),
            ),
        ),
        Rule('DQUOTE'),
    )),

]


@lang.static_init
def _init_bootstrap_grammar_rules() -> None:
    for grammar_rule_def in BOOTSTRAP_GRAMMAR_RULES:
        GrammarRule(grammar_rule_def[0], grammar_rule_def[1])


##


def not_none(x: ta.Any) -> bool:
    return x is not None


class CharValNodeVisitor(NodeVisitor):
    """CharVal node visitor."""

    def visit_char_val(self, node: Node):
        """Visit a char-val node."""

        return self.visit(node.children[0])

    def visit_case_insensitive_string(self, node: Node):
        """Visit a case-insensitive-string node."""

        value: str = next(filter(not_none, map(self.visit, node.children)))
        return Literal(value, False)

    def visit_case_sensitive_string(self, node: Node):
        """Visit a case-sensitive-string node."""

        value: str = next(filter(not_none, map(self.visit, node.children)))
        return Literal(value, True)

    @staticmethod
    def visit_quoted_string(node: Node) -> str:
        """Visit a quoted-string node."""

        return node.value[1:-1]


class NumValVisitor(NodeVisitor):
    """Visitor of num-val nodes."""

    def visit_num_val(self, node: Node):
        """Visit a num-val, returning (value, case_sensitive)."""

        return next(filter(not_none, map(self.visit, node.children)))

    def visit_bin_val(self, node: Node):
        # first child node is marker literal "b"
        return Literal(self._read_value(node.children[1:], 'BIT', 2), True)

    def visit_dec_val(self, node: Node):
        # first child node is marker literal "b"
        return Literal(self._read_value(node.children[1:], 'DIGIT', 10), True)

    def visit_hex_val(self, node: Node):
        # first child node is marker literal "x"
        return Literal(self._read_value(node.children[1:], 'HEXDIG', 16), True)

    def _read_value(
            self,
            digit_nodes: list[Node],
            digit_node_name: str,
            base: int,
    ) -> str | tuple[str, str]:
        """
        Reads the character from the child nodes of the num-val node. Returns either a string, or a tuple representing a
        character range.
        """

        # type specification needed for mypy to know that value can be either type.
        value: str | tuple[str, str]
        range_op = '-'
        buffer = ''
        iter_nodes = iter(digit_nodes)

        child_node = None
        for child_node in iter_nodes:
            if child_node.name == digit_node_name:
                buffer = buffer + child_node.value
            else:
                break

        check.not_none(child_node)

        if child_node.value == range_op:
            first_char = self._decode_bytes(buffer, base)
            buffer = ''
            for child_node in iter_nodes:
                buffer = buffer + child_node.value
            last_char = self._decode_bytes(buffer, base)
            value = (first_char, last_char)

        else:
            # either we're done, in the case of a single character, or child_node holds a concatenation operator ".", in
            # which case there are more characters to follow.
            value = self._decode_bytes(buffer, base)
            buffer = ''
            for child_node in iter_nodes:
                if child_node.name == digit_node_name:
                    buffer = buffer + child_node.value
                else:
                    value = value + self._decode_bytes(buffer, base)
                    buffer = ''

            if buffer:
                value = value + self._decode_bytes(buffer, base)

        return value

    @staticmethod
    def _decode_bytes(data: str, base: int) -> str:
        """Decodes num-val byte data. Intended to be private."""

        return chr(int(data, base=base))


class GrammarNodeVisitor(NodeVisitor):
    """Visitor for visiting nodes generated from GrammarRules."""

    def __init__(self, rule_cls: type[Rule], *args: ta.Any, **kwargs: ta.Any):
        self.rule_cls = rule_cls
        self.visit_char_val = CharValNodeVisitor()
        self.visit_num_val = NumValVisitor()

        # superclass init needs to happen here so that it will find these two methods added at runtime.
        super().__init__(*args, **kwargs)

    def visit_alternation(self, node: Node):
        """Creates an Alternation object from alternation node."""

        check.equal(node.name, 'alternation')
        args: list[Parser] = list(filter(not_none, map(self.visit, node.children)))
        return Alternation(*args) if len(args) > 1 else args[0]

    def visit_concatenation(self, node: Node):
        """Creates a Concatention object from concatenation node."""

        check.equal(node.name, 'concatenation')
        args: list[Parser] = list(filter(not_none, map(self.visit, node.children)))
        return Concatenation(*args) if len(args) > 1 else args[0]

    @staticmethod
    def visit_defined_as(node: Node):
        """Returns defined-as operator."""

        return node.value.strip()

    def visit_element(self, node: Node):
        """Creates a parser object from element node."""

        return self.visit(node.children[0])

    def visit_elements(self, node: Node):
        """Creates an Alternation object from elements node."""

        return next(filter(not_none, map(self.visit, node.children)))

    def visit_group(self, node: Node):
        """Returns an Alternation object from group node."""

        return next(filter(not_none, map(self.visit, node.children)))

    def visit_option(self, node: Node):
        """Creates an Option object from option node."""

        parser: Parser = next(filter(not_none, map(self.visit, node.children)))
        return Option(parser)

    def visit_prose_val(self, node: Node):
        """Creates a Prose parser that fails."""

        # check to see if value inside angle brackets could be a rulename. See
        # https://www.rfc-editor.org/rfc/rfc5234.html#section-2.1
        # for the explanation of this bit of hackery.
        try:
            node = GrammarRule('rulename').parse_all(node.value[1:-1])
        except ParseError:
            return Prose()
        else:
            return self.visit_rulename(node)

    @staticmethod
    def visit_repeat(node: Node):
        """Creates a Repeat object from repeat node."""

        repeat_op = '*'
        min_src = ''
        max_src = ''
        iter_child = iter(node.children)

        child = None
        for child in iter_child:
            if child.name == 'DIGIT':
                min_src = min_src + child.value
            else:
                break

        check.state(bool(child))
        if child.value == repeat_op:
            max_src = ''
            for child in iter_child:
                max_src = max_src + child.value
        else:
            max_src = min_src

        return Repeat(
            min=int(min_src, base=10) if min_src else 0,
            max=int(max_src, base=10) if max_src else None,
        )

    def visit_repetition(self, node: Node):
        """Creates a Repetition object from repetition node."""

        if node.children[0].name == 'repeat':
            return Repetition(
                self.visit_repeat(node.children[0]),
                self.visit_element(node.children[1]),
            )
        else:
            check.equal(node.children[0].name, 'element')
            return self.visit_element(node.children[0])

    def visit_rule(self, node: Node):
        """Visits a rule node, returning a Rule object."""

        rule: Rule
        defined_as: str
        elements: Parser
        rule, defined_as, elements = filter(not_none, map(self.visit, node.children))
        # this assertion tells mypy that rule should actually be an object. Without, mypy returns 'error: <nothing> has
        # no attribute "definition"'
        check.state(bool(rule))
        rule.definition = elements if defined_as == '=' else Alternation(rule.definition, elements)
        return rule

    def visit_rulelist(self, node: Node):
        """Visits a rulelist node, returning a list of Rule objects."""

        return list(filter(not_none, map(self.visit, node.children)))

    def visit_rulename(self, node: Node):
        """Visits a rulename node, looks up the Rule object for rulename, and returns it."""

        return self.rule_cls(node.value)
