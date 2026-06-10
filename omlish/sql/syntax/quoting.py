"""
Low-level identifier quoting, shared by the (DML) ``queries`` and (DDL) ``tabledefs`` renderers. Deliberately knows
nothing of either - it sits below both.
"""
from ... import dataclasses as dc
from ... import lang


##


@dc.dataclass(frozen=True)
class QuoteStyle(lang.Final):
    start: str
    end: str

    def quote(self, s: str) -> str:
        return self.start + s.replace(self.end, self.end * 2) + self.end


class QuoteStyles(lang.Namespace):
    DOUBLE = QuoteStyle('"', '"')  # ansi / standard
    BACKTICK = QuoteStyle('`', '`')
    BRACKET = QuoteStyle('[', ']')
