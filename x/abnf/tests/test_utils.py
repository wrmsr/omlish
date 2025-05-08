import typing as ta

import pytest

from ..grammars.utils import load_grammar_rulelist
from ..grammars.utils import load_grammar_rules
from ..parsers import Literal
from ..parsers import Rule as _Rule


class ImportRule(_Rule):
    pass


ImportRule('test', Literal('test'))


@load_grammar_rules([('test', ImportRule('test'))])
class Rule(_Rule):
    GRAMMAR: ta.ClassVar = []


def test_misc_load_grammar_rules_import():
    assert Rule('test').definition == ImportRule('test').definition


@load_grammar_rulelist([('test', ImportRule('test'))])
class Rule1(_Rule):
    GRAMMAR = ''


def test_load_grammar():
    assert Rule('test').definition == ImportRule('test').definition


class Foo(_Rule):
    GRAMMAR = 'foo="bar"'


def test_load_grammar_rules_str():
    with pytest.raises(TypeError):
        load_grammar_rules()(Foo)
