"""
Collected rules from RFC 8187
https://tools.ietf.org/html/rfc8187
"""
import typing as ta

from ..parsers import Rule as _Rule
from . import rfc5646
from .utils import load_grammar_rules


##


@load_grammar_rules([
    ('language', rfc5646.Rule('Language-Tag')),
])
class Rule(_Rule):
    """Rules from RFC 8187."""

    GRAMMAR: ta.ClassVar[list[str] | str] = [
        'ext-value = charset "\'" [ language ] "\'" value-chars',
        'charset = "UTF-8" / mime-charset',
        'mime-charset = 1*mime-charsetc',
        'mime-charsetc = ALPHA / DIGIT  / "!" / "#" / "$" / "%" / "&"  / "+" / "-" / "^" / "_" / "`"  / "{" / "}" / "~"',  # noqa
        # language = <Language-Tag, see [RFC5646], Section 2.1>
        'value-chars = *( pct-encoded / attr-char )',
        'pct-encoded = "%" HEXDIG HEXDIG',
        'attr-char = ALPHA / DIGIT  / "!" / "#" / "$" / "&" / "+" / "-" / "."  / "^" / "_" / "`" / "|" / "~"  ',
    ]
