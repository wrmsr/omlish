class JmespathError(ValueError):
    pass


class ParseError(JmespathError):
    _ERROR_MESSAGE = 'Invalid jmespath expression'

    def __init__(
            self,
            lex_position,
            token_value,
            token_type,
            msg=_ERROR_MESSAGE,
    ):
        super().__init__(lex_position, token_value, token_type)
        self.lex_position = lex_position
        self.token_value = token_value
        self.token_type = token_type.upper()
        self.msg = msg
        # Whatever catches the ParseError can fill in the full expression
        self.expression = None

    def __str__(self):
        # self.lex_position +1 to account for the starting double quote char.
        underline = ' ' * (self.lex_position + 1) + '^'
        return (
            f'{self.msg}: Parse error at column {self.lex_position}, '
            f'token "{self.token_value}" ({self.token_type}), for expression:\n"{self.expression}"\n{underline}'
        )


class IncompleteExpressionError(ParseError):
    def set_expression(self, expression):
        self.expression = expression
        self.lex_position = len(expression)
        self.token_type = None
        self.token_value = None

    def __str__(self):
        # self.lex_position +1 to account for the starting double quote char.
        underline = ' ' * (self.lex_position + 1) + '^'
        return (
            f'Invalid jmespath expression: Incomplete expression:\n'
            f'"{self.expression}"\n{underline}'
        )


class LexerError(ParseError):
    def __init__(self, lexer_position, lexer_value, message, expression=None):
        self.lexer_position = lexer_position
        self.lexer_value = lexer_value
        self.message = message
        super().__init__(lexer_position, lexer_value, message)
        # Whatever catches LexerError can set this.
        self.expression = expression

    def __str__(self):
        underline = ' ' * self.lexer_position + '^'
        return f'Bad jmespath expression: {self.message}:\n{self.expression}\n{underline}'


class ArityError(ParseError):
    def __init__(self, expected, actual, name):
        self.expected_arity = expected
        self.actual_arity = actual
        self.function_name = name
        self.expression = None

    def __str__(self):
        return (
            f"Expected {self.expected_arity} {self._pluralize('argument', self.expected_arity)} "
            f'for function {self.function_name}(), received {self.actual_arity}'
        )

    def _pluralize(self, word, count):
        if count == 1:
            return word
        else:
            return word + 's'


class VariadicArityError(ArityError):
    def __str__(self):
        return (
            f"Expected at least {self.expected_arity} {self._pluralize('argument', self.expected_arity)} "
            f'for function {self.function_name}(), received {self.actual_arity}'
        )


class JmespathTypeError(JmespathError):
    def __init__(
            self,
            function_name,
            current_value,
            actual_type,
            expected_types,
    ):
        self.function_name = function_name
        self.current_value = current_value
        self.actual_type = actual_type
        self.expected_types = expected_types

    def __str__(self):
        return (
            f'In function {self.function_name}(), invalid type for value: {self.current_value}, '
            f'expected one of: {self.expected_types}, received: "{self.actual_type}"'
        )


class JmespathValueError(JmespathError):
    def __init__(
            self,
            function_name,
            current_value,
            expected_types,
    ):
        self.function_name = function_name
        self.current_value = current_value
        self.expected_types = expected_types

    def __str__(self):
        return (
            f'In function {self.function_name}(), invalid value: "{self.current_value}", '
            f'expected: {self.expected_types}'
        )


class EmptyExpressionError(JmespathError):
    def __init__(self):
        super().__init__('Invalid Jmespath expression: cannot be empty.')


class UnknownFunctionError(JmespathError):
    pass


class UndefinedVariableError(JmespathError):
    def __init__(self, varname):
        self.varname = varname
        super().__init__(f'Reference to undefined variable: {self.varname}')
