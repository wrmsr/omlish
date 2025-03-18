import typing as ta

from .errors import ParseError
from .values import Char
from .values import Map
from .values import NIL
from .values import Nil
from .values import Set
from .values import Symbol
from .values import Tagged
from .values import Value
from .values import Vector


##


class Parser:
    def __init__(self, stream: ta.TextIO) -> None:
        super().__init__()

        self._stream = stream
        self._current_char: str | None = None
        self._position = 0
        self._advance()

    def _advance(self) -> None:
        self._current_char = self._stream.read(1)
        self._position += 1

    def _skip_whitespace(self) -> None:
        while self._current_char and (self._current_char.isspace() or self._current_char == ',' or self._current_char == ';'):
            if self._current_char == ';':
                # Skip until newline
                while self._current_char and self._current_char != '\n':
                    self._advance()
            self._advance()

    def _peek(self) -> str | None:
        pos = self._stream.tell()
        char = self._stream.read(1)
        self._stream.seek(pos)
        return char

    def parse(self) -> Value:
        self._skip_whitespace()

        if not self._current_char:
            raise ParseError('Unexpected end of input')

        # Handle basic values
        if self._current_char == 'n' and self._peek() == 'i':  # nil
            return self._parse_nil()
        elif self._current_char in ('t', 'f'):  # true/false
            return self._parse_boolean()
        elif self._current_char == '"':  # string
            return self._parse_string()
        elif self._current_char == '\\':  # character
            return self._parse_char()
        elif self._current_char == ':':  # keyword (treated as Symbol)
            return self._parse_keyword()
        elif self._current_char == '#':  # set or tagged
            self._advance()
            if not self._current_char:
                raise ParseError('Unexpected end of input after #')
            if self._current_char == '{':
                return self._parse_set()
            else:
                return self._parse_tagged()
        elif self._current_char == '[':  # vector
            return self._parse_vector()
        elif self._current_char == '{':  # map
            return self._parse_map()
        elif self._current_char == '(':  # list (treated as Vector)
            return self._parse_list()
        elif self._current_char == '-' or self._current_char.isdigit():  # number
            return self._parse_number()
        else:  # symbol
            return self._parse_symbol()

    def _parse_nil(self) -> Nil:
        value = ''
        while self._current_char and self._current_char.isalpha():
            value += self._current_char
            self._advance()
        if value != 'nil':
            raise ParseError(f"Expected 'nil', got '{value}'")
        return NIL

    def _parse_boolean(self) -> bool:
        value = ''
        while self._current_char and self._current_char.isalpha():
            value += self._current_char
            self._advance()
        if value == 'true':
            return True
        elif value == 'false':
            return False
        raise ParseError(f"Expected 'true' or 'false', got '{value}'")

    def _parse_string(self) -> str:
        self._advance()  # Skip opening quote
        result = ''
        escaped = False

        while self._current_char:
            if escaped:
                if self._current_char == 'n':
                    result += '\n'
                elif self._current_char == 't':
                    result += '\t'
                elif self._current_char == 'r':
                    result += '\r'
                elif self._current_char == '\\':
                    result += '\\'
                elif self._current_char == '"':
                    result += '"'
                else:
                    raise ParseError(f'Invalid escape sequence: \\{self._current_char}')
                escaped = False
            elif self._current_char == '\\':
                escaped = True
            elif self._current_char == '"':
                self._advance()
                return result
            else:
                result += self._current_char
            self._advance()

        raise ParseError('Unterminated string')

    def _parse_char(self) -> Char:
        self._advance()  # Skip backslash
        if not self._current_char:
            raise ParseError('Unexpected end of input after \\')

        special_chars = {
            'newline': '\n',
            'return': '\r',
            'space': ' ',
            'tab': '\t'
        }

        # Check for special characters
        for name, char in special_chars.items():
            if self._current_char == name[0]:
                test_pos = self._stream.tell()
                test = self._current_char
                for _ in range(len(name) - 1):
                    next_char = self._stream.read(1)
                    if not next_char:
                        break
                    test += next_char
                if test == name:
                    self._stream.seek(test_pos)
                    for _ in range(len(name)):
                        self._advance()
                    return Char(char)
                self._stream.seek(test_pos)

        # Regular character
        char = self._current_char
        self._advance()
        return Char(char)

    def _parse_symbol(self) -> Symbol:
        name = ''
        while self._current_char and (self._current_char.isalnum() or self._current_char in '.*+!-_?$%&=<>/:'):
            name += self._current_char
            self._advance()

        if '/' in name:
            namespace, name = name.split('/', 1)
            return Symbol(name=name, namespace=namespace)
        return Symbol(name=name)

    def _parse_keyword(self) -> Symbol:
        self._advance()  # Skip :
        return self._parse_symbol()

    def _parse_vector(self) -> Vector:
        self._advance()  # Skip [
        values = []
        
        while self._current_char:
            self._skip_whitespace()
            if self._current_char == ']':
                self._advance()
                return Vector(values)
            values.append(self.parse())
            self._skip_whitespace()

        raise ParseError('Unterminated vector')

    def _parse_map(self) -> Map:
        self._advance()  # Skip {
        entries = []
        
        while self._current_char:
            self._skip_whitespace()
            if self._current_char == '}':
                self._advance()
                return Map(entries)
            
            key = self.parse()
            self._skip_whitespace()
            if not self._current_char:
                raise ParseError('Unexpected end of input in map')
            
            value = self.parse()
            entries.append((key, value))
            self._skip_whitespace()

        raise ParseError('Unterminated map')

    def _parse_set(self) -> Set:
        self._advance()  # Skip {
        values = []
        
        while self._current_char:
            self._skip_whitespace()
            if self._current_char == '}':
                self._advance()
                return Set(values)
            values.append(self.parse())
            self._skip_whitespace()

        raise ParseError('Unterminated set')

    def _parse_list(self) -> Vector:
        self._advance()  # Skip (
        values = []
        
        while self._current_char:
            self._skip_whitespace()
            if self._current_char == ')':
                self._advance()
                return Vector(values)
            values.append(self.parse())
            self._skip_whitespace()

        raise ParseError('Unterminated list')

    def _parse_tagged(self) -> Tagged:
        tag = self._parse_symbol()
        self._skip_whitespace()
        if not self._current_char:
            raise ParseError('Unexpected end of input after tag')
        value = self.parse()
        return Tagged(tag=tag, value=value)

    def _parse_number(self) -> ta.Union[int, float]:
        num_str = ''
        is_float = False
        
        # Handle sign
        if self._current_char == '-':
            num_str += self._current_char
            self._advance()
        
        # Parse digits and decimal point
        while self._current_char and (self._current_char.isdigit() or self._current_char in '.eE'):
            if self._current_char in '.eE':
                is_float = True
            num_str += self._current_char
            self._advance()

        try:
            if is_float:
                return float(num_str)
            return int(num_str)
        except ValueError:
            raise ParseError(f'Invalid number format: {num_str}')
