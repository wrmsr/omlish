import json
import string
import typing as ta
import warnings

from .exceptions import EmptyExpressionError
from .exceptions import LexerError


class Lexer:
    START_IDENTIFIER: ta.AbstractSet[str] = set(string.ascii_letters + '_')
    VALID_IDENTIFIER: ta.AbstractSet[str] = set(string.ascii_letters + string.digits + '_')

    VALID_NUMBER: ta.AbstractSet[str] = set(string.digits)

    WHITESPACE: ta.AbstractSet[str] = set(' \t\n\r')

    SIMPLE_TOKENS: ta.Mapping[str, str] = {
        '.': 'dot',
        '*': 'star',
        ']': 'rbracket',
        ',': 'comma',
        ':': 'colon',
        '@': 'current',
        '(': 'lparen',
        ')': 'rparen',
        '{': 'lbrace',
        '}': 'rbrace',
        '+': 'plus',
        '%': 'modulo',
        '\u2212': 'minus',
        '\u00d7': 'multiply',
        '\u00f7': 'divide',
    }

    def __init__(self):
        self._enable_legacy_literals = False

    def tokenize(self, expression, options=None):
        if options is not None:
            self._enable_legacy_literals = options.enable_legacy_literals

        self._initialize_for_expression(expression)
        while self._current is not None:
            if self._current in self.SIMPLE_TOKENS:
                yield {
                    'type': self.SIMPLE_TOKENS[self._current],
                    'value': self._current,
                    'start': self._position,
                    'end': self._position + 1,
                }
                self._next()

            elif self._current in self.START_IDENTIFIER:
                start = self._position

                buff = self._current
                while self._next() in self.VALID_IDENTIFIER:
                    buff += self._current

                yield {
                    'type': 'unquoted_identifier',
                    'value': buff,
                    'start': start,
                    'end': start + len(buff),
                }

            elif self._current in self.WHITESPACE:
                self._next()

            elif self._current == '[':
                start = self._position

                next_char = self._next()
                if next_char == ']':
                    self._next()
                    yield {
                        'type': 'flatten',
                        'value': '[]',
                        'start': start,
                        'end': start + 2,
                    }

                elif next_char == '?':
                    self._next()
                    yield {
                        'type': 'filter',
                        'value': '[?',
                        'start': start,
                        'end': start + 2,
                    }

                else:
                    yield {
                        'type': 'lbracket',
                        'value': '[',
                        'start': start,
                        'end': start + 1,
                    }

            elif self._current == "'":
                yield self._consume_raw_string_literal()

            elif self._current == '|':
                yield self._match_or_else('|', 'or', 'pipe')

            elif self._current == '&':
                yield self._match_or_else('&', 'and', 'expref')

            elif self._current == '`':
                yield self._consume_literal()

            elif self._current in self.VALID_NUMBER:
                start = self._position

                buff = self._consume_number()
                yield {
                    'type': 'number',
                    'value': int(buff),
                    'start': start,
                    'end': start + len(buff),
                }

            elif self._current == '-':
                if not self._peek_is_next_digit():
                    self._next()
                    yield {
                        'type': 'minus',
                        'value': '-',
                        'start': self._position - 1,
                        'end': self._position,
                    }
                else:
                    # Negative number.
                    start = self._position
                    buff = self._consume_number()
                    if len(buff) > 1:
                        yield {
                            'type': 'number',
                            'value': int(buff),
                            'start': start,
                            'end': start + len(buff),
                        }
                    else:
                        raise LexerError(
                            lexer_position=start,
                            lexer_value=buff,
                            message=f"Unknown token '{buff}'")

            elif self._current == '/':
                self._next()
                if self._current == '/':
                    self._next()
                    yield {
                        'type': 'div',
                        'value': '//',
                        'start': self._position - 1,
                        'end': self._position,
                    }
                else:
                    yield {
                        'type': 'divide',
                        'value': '/',
                        'start': self._position,
                        'end': self._position + 1,
                    }

            elif self._current == '"':
                yield self._consume_quoted_identifier()

            elif self._current == '<':
                yield self._match_or_else('=', 'lte', 'lt')

            elif self._current == '>':
                yield self._match_or_else('=', 'gte', 'gt')

            elif self._current == '!':
                yield self._match_or_else('=', 'ne', 'not')

            elif self._current == '=':
                yield self._match_or_else('=', 'eq', 'assign')

            elif self._current == '$':
                if self._peek_may_be_valid_unquoted_identifier():
                    yield self._consume_variable()
                else:
                    yield {
                        'type': 'root',
                        'value': self._current,
                        'start': self._position,
                        'end': self._position + 1,
                    }
                    self._next()
            else:
                raise LexerError(
                    lexer_position=self._position,
                    lexer_value=self._current,
                    message=f'Unknown token {self._current})',
                )

        yield {
            'type': 'eof',
            'value': '',
            'start': self._length,
            'end': self._length,
        }

    def _consume_number(self):
        start = self._position  # noqa

        buff = self._current
        while self._next() in self.VALID_NUMBER:
            buff += self._current
        return buff

    def _consume_variable(self):
        start = self._position

        buff = self._current
        self._next()
        if self._current not in self.START_IDENTIFIER:
            raise LexerError(
                lexer_position=start,
                lexer_value=self._current,
                message=f'Invalid variable starting character {self._current}',
            )

        buff += self._current
        while self._next() in self.VALID_IDENTIFIER:
            buff += self._current

        return {
            'type': 'variable',
            'value': buff,
            'start': start,
            'end': start + len(buff),
        }

    def _peek_may_be_valid_unquoted_identifier(self):
        if (self._position == self._length - 1):
            return False
        else:
            nxt = self._chars[self._position + 1]
            return nxt in self.START_IDENTIFIER

    def _peek_is_next_digit(self):
        if (self._position == self._length - 1):
            return False
        else:
            nxt = self._chars[self._position + 1]
            return nxt in self.VALID_NUMBER

    def _initialize_for_expression(self, expression):
        if not expression:
            raise EmptyExpressionError
        self._position = 0
        self._expression = expression
        self._chars = list(self._expression)
        self._current = self._chars[self._position]
        self._length = len(self._expression)

    def _next(self):
        if self._position == self._length - 1:
            self._current = None
        else:
            self._position += 1
            self._current = self._chars[self._position]
        return self._current

    def _consume_until(self, delimiter):
        # Consume until the delimiter is reached, allowing for the delimiter to be escaped with "\".
        start = self._position

        buff = ''
        self._next()
        while self._current != delimiter:
            if self._current == '\\':
                buff += '\\'
                self._next()

            if self._current is None:
                # We're at the EOF.
                raise LexerError(
                    lexer_position=start,
                    lexer_value=self._expression[start:],
                    message=f'Unclosed {delimiter} delimiter',
                )

            buff += self._current
            self._next()

        # Skip the closing delimiter.
        self._next()
        return buff

    def _consume_literal(self):
        start = self._position

        token = self._consume_until('`')
        lexeme = token.replace('\\`', '`')
        parsed_json = None
        try:
            # Assume it is valid JSON and attempt to parse.
            parsed_json = json.loads(lexeme)
        except ValueError:
            error = LexerError(
                lexer_position=start,
                lexer_value=self._expression[start:],
                message=f'Bad token %s `{token}`',
            )

            if not self._enable_legacy_literals:
                raise error  # noqa

            try:
                # Invalid JSON values should be converted to quoted JSON strings during the JEP-12 deprecation period.
                parsed_json = json.loads('"%s"' % lexeme.lstrip())  # noqa
                warnings.warn('deprecated string literal syntax', DeprecationWarning)
            except ValueError:
                raise LexerError(  # noqa
                    lexer_position=start,
                    lexer_value=self._expression[start:],
                    message=f'Bad token {lexeme}',
                )

        token_len = self._position - start
        return {
            'type': 'literal',
            'value': parsed_json,
            'start': start,
            'end': token_len,
        }

    def _consume_quoted_identifier(self):
        start = self._position

        lexeme = '"' + self._consume_until('"') + '"'
        try:
            token_len = self._position - start
            return {
                'type': 'quoted_identifier',
                'value': json.loads(lexeme),
                'start': start,
                'end': token_len,
            }

        except ValueError as e:
            error_message = str(e).split(':')[0]
            raise LexerError(  # noqa
                lexer_position=start,
                lexer_value=lexeme,
                message=error_message,
            )

    def _consume_raw_string_literal(self):
        start = self._position

        lexeme = self._consume_until("'") \
            .replace("\\'", "'")  \
            .replace('\\\\', '\\')

        token_len = self._position - start
        return {
            'type': 'literal',
            'value': lexeme,
            'start': start,
            'end': token_len,
        }

    def _match_or_else(self, expected, match_type, else_type):
        start = self._position

        current = self._current
        next_char = self._next()
        if next_char == expected:
            self._next()
            return {
                'type': match_type,
                'value': current + next_char,
                'start': start,
                'end': start + 1,
            }

        return {
            'type': else_type,
            'value': current,
            'start': start,
            'end': start,
        }
