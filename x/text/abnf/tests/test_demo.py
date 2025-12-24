import pytest

from omextra.text.abnf.utils import fix_ws

from ..core import GrammarNodeVisitor
from ..core import GrammarRule
from ..errors import ParseError
from ..parsers import Rule


@pytest.mark.skip_unless_alone
def test_demo():
    with open('omextra/text/abnf/tests/demo.abnf') as f:
        rule_source = fix_ws(f.read())

    grule = GrammarRule('rulelist')
    try:
        parse_tree, start = grule.parse(rule_source, 0)
    except ParseError:
        raise

    visitor = GrammarNodeVisitor(Rule)

    rule = visitor.visit(parse_tree)

    with open('omextra/text/abnf/tests/demo.txt') as f:
        demo_source = fix_ws(f.read())

    print(rule.parse_all(demo_source))
