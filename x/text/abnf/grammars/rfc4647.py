"""
Collected rules from RFC 4647
https://tools.ietf.org/html/rfc4647
"""
import typing as ta

from ..parsers import Rule as _Rule
from .utils import load_grammar_rules


##


@load_grammar_rules()
class Rule(_Rule):
    """Rule objects generated from ABNF in RFC 4647."""

    GRAMMAR: ta.ClassVar[list[str] | str] = [
        'language-range = (1*8ALPHA *("-" 1*8alphanum)) / "*"',
        'alphanum = ALPHA / DIGIT',
        'extended-language-range = (1*8ALPHA / "*") *("-" (1*8alphanum / "*"))',
    ]
