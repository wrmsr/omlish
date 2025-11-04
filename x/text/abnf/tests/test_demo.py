from ..core import GrammarNodeVisitor
from ..core import GrammarRule
from ..errors import ParseError
from ..parsers import Rule



def test_demo():
    with open('omextra/text/abnf/tests/demo.abnf') as f:
        rule_source = f.read()

    if rule_source[-2:] != '\r\n':
        rule_source = rule_source + '\r\n'
    grule = GrammarRule('rule')
    try:
        parse_tree, start = grule.parse(rule_source, 0)
    except ParseError:
        raise
    visitor = GrammarNodeVisitor(Rule)
    rule = visitor.visit(parse_tree)

    print(rule.parse_all('barf'))
