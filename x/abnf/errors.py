import typing as ta


if ta.TYPE_CHECKING:
    from .parsers import Parser


##


class ParseError(Exception):
    """Raised in response to errors during parsing."""

    def __init__(self, parser: 'Parser', start: int, *args: ta.Any) -> None:
        super().__init__()

        # it turns out that calling super().__init__(*args) is quite slow. Because ParseError objects are created so
        # often, the slowness adds up. So we just set self.args directly, which is all that Exception.__init__ does.
        self.args = args
        self.parser = parser
        self.start = start

    def __str__(self):
        return f'{self.parser!s}: {self.start}'


class GrammarError(Exception):
    """Raised in response to errors detected in the grammar."""
