"""
This is the extension to RFC 5234 which adds case-sensitive char-val.

Collected rules from RFC 7405
https://tools.ietf.org/html/rfc7405
"""
import typing as ta

from ..parsers import Rule as _Rule
from . import rfc5234
from .utils import load_grammar_rules


##


@load_grammar_rules([
    (rule.name, rule)
    for rule in rfc5234.Rule.rules()
    if rule.name not in {core_rule.name for core_rule in _Rule.rules()}
])
class Rule(_Rule):
    """Rule objects generated from ABNF in RFC 7405."""

    GRAMMAR: ta.ClassVar[list[str] | str] = [
        'char-val = case-insensitive-string / case-sensitive-string',
        'case-insensitive-string = [ "%i" ] quoted-string',
        'case-sensitive-string = "%s" quoted-string',
        'quoted-string  =  DQUOTE *(%x20-21 / %x23-7E) DQUOTE\
                                ; quoted string of SP and VCHAR\
                                ;  without DQUOTE',
    ]
