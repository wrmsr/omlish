"""
https://github.com/golang/go/blob/3d33437c450aa74014ea1d41cd986b6ee6266984/src/text/template/parse/lex.go
"""
# Copyright 2009 The Go Authors.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#      disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#      following disclaimer in the documentation and/or other materials provided with the distribution.
#    * Neither the name of Google LLC nor the names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import dataclasses as dc
import enum
import string
import typing as ta


class TokenType(enum.IntEnum):
    ERROR = enum.auto()          # error occurred; value is text of error
    BOOL = enum.auto()           # boolean constant
    CHAR = enum.auto()           # printable ASCII character; grab bag for comma etc.
    CHAR_CONSTANT = enum.auto()  # character constant
    COMMENT = enum.auto()        # comment text
    COMPLEX = enum.auto()        # complex constant (1+2i); imaginary is just a number
    ASSIGN = enum.auto()         # equals ('=') introducing an assignment
    DECLARE = enum.auto()        # colon-equals (':=') introducing a declaration
    EOF = enum.auto()
    FIELD = enum.auto()          # alphanumeric identifier starting with '.'
    IDENTIFIER = enum.auto()     # alphanumeric identifier not starting with '.'
    LEFT_DELIM = enum.auto()     # left action delimiter
    LEFT_PAREN = enum.auto()     # '(' inside action
    NUMBER = enum.auto()         # simple number, including imaginary
    PIPE = enum.auto()           # pipe symbol
    RAW_STRING = enum.auto()     # raw quoted string (includes quotes)
    RIGHT_DELIM = enum.auto()    # right action delimiter
    RIGHT_PAREN = enum.auto()    # ')' inside action
    SPACE = enum.auto()          # run of spaces separating arguments
    STRING = enum.auto()         # quoted string (includes quotes)
    TEXT = enum.auto()           # plain text
    VARIABLE = enum.auto()       # variable starting with '$', such as '$' or  '$1' or '$hello'

    # Keywords appear after all the rest.
    KEYWORD = enum.auto()   # used only to delimit the keywords
    BLOCK = enum.auto()     # block keyword
    BREAK = enum.auto()     # break keyword
    CONTINUE = enum.auto()  # continue keyword
    DOT = enum.auto()       # the cursor, spelled '.'
    DEFINE = enum.auto()    # define keyword
    ELSE = enum.auto()      # else keyword
    END = enum.auto()       # end keyword
    IF = enum.auto()        # if keyword
    NIL = enum.auto()       # the untyped nil constant, easiest to treat as a keyword
    RANGE = enum.auto()     # range keyword
    TEMPLATE = enum.auto()  # template keyword
    WITH = enum.auto()      # with keyword


TOKEN_TYPE_MAP: ta.Mapping[str, TokenType] = {
    '.': TokenType.DOT,
    'block': TokenType.BLOCK,
    'break': TokenType.BREAK,
    'continue': TokenType.CONTINUE,
    'define': TokenType.DEFINE,
    'else': TokenType.ELSE,
    'end': TokenType.END,
    'if': TokenType.IF,
    'range': TokenType.RANGE,
    'nil': TokenType.NIL,
    'template': TokenType.TEMPLATE,
    'with': TokenType.WITH,
}


@dc.dataclass(frozen=True)
class Token:
    typ: TokenType
    pos:  int
    val:  str
    line: int


SPACE_CHARS = ' \t\r\n'  # These are the space characters defined by Go itself.
TRIM_MARKER = '-'  # Attached to left/right delimiter, trims trailing spaces from preceding/following text.
TRIM_MARKER_LEN = 1 + 1  # marker plus space before or after


@dc.dataclass(frozen=True, kw_only=True)
class LexOptions:
    emit_comment: bool = False
    break_ok: bool = False
    continue_ok: bool = False


StateFn: ta.TypeAlias = ta.Callable[[], ta.Optional['StateFn']]

LEFT_DELIM = '{{'
RIGHT_DELIM = '}}'
LEFT_COMMENT = '/*'
RIGHT_COMMENT = '*/'

EOF = ''


class Lexer:
    def __init__(
            self,
            name: str,
            input: str,
            options: LexOptions = LexOptions(),
            *,
            left_delim: str = LEFT_DELIM,
            right_delim: str = RIGHT_DELIM,
    ) -> None:
        super().__init__()

        self._name = name  # the name of the input; used only for error reports
        self._input = input  # the string being scanned
        self._left_delim = left_delim  # start of action marker
        self._right_delim = right_delim  # end of action marker
        self._options = options

        self._pos = 0  # current position in the input
        self._start = 0  # start position of this token
        self._at_eof = False  # we have hit the end of input and returned eof
        self._paren_depth = 0  # nesting depth of ( ) exprs
        self._line = 1  # 1+number of newlines seen
        self._start_line = 1  # start line of this token
        self._inside_action = False  # are we inside an action?

        self._token: Token = Token(TokenType.EOF, 0, 'EOF', 0)  # token to return to parser

    def next(self) -> str:
        # returns the next rune in the input.
        if self._pos >= len(self._input):
            self._at_eof = True
            return EOF

        r = self._input[self._pos]
        self._pos += 1
        if r == '\n':
            self._line += 1
        return r

    def peek(self) -> str:
        # peek returns but does not consume the next rune in the input.
        r = self.next()
        self.backup()
        return r

    def backup(self) -> None:
        # backup steps back one rune.
        if not self._at_eof and self._pos > 0:
            r = self._input[self._pos - 1]
            self._pos -= 1
            # Correct newline count.
            if r == '\n':
                self._line -= 1

    def this_token(self, t: TokenType) -> Token:
        # this_token returns the token at the current input point with the specified type and advances the input.
        i = Token(t, self._start, self._input[self._start:self._pos], self._start_line)
        self._start = self._pos
        self._start_line = self._line
        return i

    def emit(self, t: TokenType) -> StateFn | None:
        # emit passes the trailing text as an token back to the parser.
        return self.emit_token(self.this_token(t))

    def emit_token(self, i: Token) -> StateFn | None:
        # emit_token passes the specified token to the parser.
        self._token = i
        return None

    def ignore(self) -> None:
        # ignore skips over the pending input before this point. It tracks newlines in the ignored text, so use it only
        # for text that is skipped without calling self.next.
        self._line += self._input[self._start:self._pos].count('\n')
        self._start = self._pos
        self._start_line = self._line

    def accept(self, valid: str) -> bool:
        # accept consumes the next rune if it's from the valid set.
        if self.next() in valid:
            return True
        self.backup()
        return False

    def accept_run(self, valid: str) -> None:
        # accept_run consumes a run of runes from the valid set.
        while self.next() in valid:
            pass
        self.backup()

    def error(self, fmt: str, *args: ta.Any) -> StateFn | None:
        # error returns an error token and terminates the scan by passing back a nil pointer that will be the next
        # state, terminating self._next_token.
        self._token = Token(TokenType.ERROR, self._start, fmt % args, self._start_line)
        self._start = 0
        self._pos = 0
        self._input = self._input[:0]
        return None

    def next_token(self) -> Token:
        # next_token returns the next token from the input. Called by the parser, not in the lexing goroutine.
        self._token = Token(TokenType.EOF, self._pos, 'EOF', self._start_line)
        state: StateFn = self._lex_text
        if self._inside_action:
            state = self._lex_inside_action
        while True:
            state = state(self)
            if state is None:
                return self._token

    # state functions

    def _lex_text(self) -> StateFn:
        # _lex_text scans until an opening action delimiter, '{{'.
        if (x := self._input[self._pos:].find(self._left_delim)) >= 0:
            if x > 0:
                self._pos += x
                # Do we trim any trailing space?
                trim_length = 0
                delim_end = self._pos + len(self._left_delim)
                if has_left_trim_marker(self._input[delim_end:]):
                    trim_length = right_trim_length(self._input[self._start:self._pos])
                self._pos -= trim_length
                self._line += self._input[self._start:self._pos].count('\n')
                i = self.this_token(TokenType.TEXT)
                self._pos += trim_length
                self.ignore()
                if len(i.val) > 0:
                    return self.emit_token(i)

            return self._lex_left_delim

        self._pos = len(self._input)
        # Correctly reached EOF.
        if self._pos > self._start:
            self._line += self._input[self._start:self._pos].count('\n')
            return self.emit(TokenType.TEXT)

        return self.emit(TokenType.EOF)

    def at_right_delim(self) -> tuple[bool, bool]:  # (delim, trim_space)
        # at_right_delim reports whether the lexer is at a right delimiter, possibly preceded by a trim marker.
        if (
                has_right_trim_marker(self._input[self._pos:]) and
                self._input[self._pos + TRIM_MARKER_LEN:].startswith(self._right_delim)
        ):
            # With trim marker.
            return True, True
        if self._input[self._pos:].startswith(self._right_delim):
            # Without trim marker.
            return True, False
        return False, False

    def _lex_left_delim(self) -> StateFn:
        # _lex_left_delim scans the left delimiter, which is known to be present, possibly with a trim marker. (The text
        # to be trimmed has already been emitted.)
        self._pos += len(self._left_delim)
        trim_space = has_left_trim_marker(self._input[self._pos:])
        after_marker = 0
        if trim_space:
            after_marker = TRIM_MARKER_LEN
        if self._input[self._pos+after_marker:].startswith(LEFT_COMMENT):
            self._pos += after_marker
            self.ignore()
            return self._lex_comment
        i = self.this_token(TokenType.LEFT_DELIM)
        self._inside_action = True
        self._pos += after_marker
        self.ignore()
        self._paren_depth = 0
        return self.emit_token(i)

    def _lex_comment(self) -> StateFn:
        # _lex_comment scans a comment. The left comment marker is known to be present.
        self._pos += len(LEFT_COMMENT)
        x = self._input[self._pos:].find(RIGHT_COMMENT)
        if x < 0:
            return self.error('unclosed comment')
        self._pos += x + len(RIGHT_COMMENT)
        delim, trim_space = self.at_right_delim()
        if not delim:
            return self.error('comment ends before closing delimiter')
        i = self.this_token(TokenType.COMMENT)
        if trim_space:
            self._pos += TRIM_MARKER_LEN
        self._pos += len(self._right_delim)
        if trim_space:
            self._pos += left_trim_length(self._input[self._pos:])
        self.ignore()
        if self._options.emit_comment:
            return self.emit_token(i)
        return self._lex_text

    def _lex_right_delim(self) -> StateFn:
        # _lex_right_delim scans the right delimiter, which is known to be present, possibly with a trim marker.
        _, trim_space = self.at_right_delim()
        if trim_space:
            self._pos += TRIM_MARKER_LEN
            self.ignore()
        self._pos += len(self._right_delim)
        i = self.this_token(TokenType.RIGHT_DELIM)
        if trim_space:
            self._pos += left_trim_length(self._input[self._pos:])
            self.ignore()
        self._inside_action = False
        return self.emit_token(i)

    def _lex_inside_action(self) -> StateFn:
        # _lex_inside_action scans the elements inside action delimiters. Either number, quoted string, or identifier.
        # Spaces separate arguments; runs of spaces turn into itemSpace. Pipe symbols separate and are emitted.
        delim, _ = self.at_right_delim()
        if delim:
            if self._paren_depth == 0:
                return self._lex_right_delim
            return self.error('unclosed left paren')
        r = self.next()
        if r == EOF:
            return self.error('unclosed action')
        elif is_space(r):
            self.backup()  # Put space back in case we have ' -}}'.
            return self._lex_space
        elif r == '=':
            return self.emit(TokenType.ASSIGN)
        elif r == ':':
            if self.next() != '=':
                return self.error('expected :=')
            return self.emit(TokenType.DECLARE)
        elif r == '|':
            return self.emit(TokenType.PIPE)
        elif r == '"':
            return self._lex_quote
        elif r == '`':
            return self._lex_raw_quote
        elif r == '$':
            return self._lex_variable
        elif r == '\'':
            return self._lex_char
        elif r == '.':
            # special look-ahead for '.field' so we don't break self._backup().
            if self._pos < len(self._input):
                r = self._input[self._pos]
                if r < '0' or '9' < r:
                    return self._lex_field
            # '.' can start a number.
            self.backup()
            return self._lex_number
        elif r == '+' or r == '-' or ('0' <= r and r <= '9'):
            self.backup()
            return self._lex_number
        elif is_alpha_numeric(r):
            self.backup()
            return self._lex_identifier
        elif r == '(':
            self._paren_depth += 1
            return self.emit(TokenType.LEFT_PAREN)
        elif r == ')':
            self._paren_depth -= 1
            if self._paren_depth < 0:
                return self.error('unexpected right paren')
            return self.emit(TokenType.RIGHT_PAREN)
        elif r <= unicode.MaxASCII and unicode.IsPrint(r):
            return self.emit(TokenType.CHAR)
        else:
            return self.error('unrecognized character in action: %r', r)

    def _lex_pace(self) -> StateFn:
        # _lex_space scans a run of space characters. We have not consumed the first space, which is known to be
        # present. Take care if there is a trim-marked right delimiter, which starts with a space.
        num_spaces = 0
        while True:
            r = self.peek()
            if not is_space(r):
                break
            self.next()
            num_spaces += 1
        # Be careful about a trim-marked closing delimiter, which has a minus after a space. We know there is a space,
        # so check for the '-' that might follow.
        if (
                has_right_trim_marker(self._input[self._pos - 1:]) and
                self._input[self._pos - 1 + TRIM_MARKER_LEN:].startswith(self._right_delim)
        ):
            self.backup()  # Before the space.
            if num_spaces == 1:
                return self._lex_right_delim  # On the delim, so go right to that.
        return self.emit(TokenType.SPACE)

    def _lex_identifier(self) -> StateFn:
        # _lex_identifier scans an alphanumeric.
        while True:
            r = self.next()
            if is_alpha_numeric(r):
                # absorb.
                pass
            else:
                self.backup()
                word = self._input[self._start:self._pos]
                if not self.at_terminator():
                    return self.error('bad character %r', r)
                if TOKEN_TYPE_MAP[word] > TokenType.KEYWORD:
                    item = TOKEN_TYPE_MAP[word]
                    if (
                            (item == TokenType.BREAK and not self._options.break_ok) or
                            (item == TokenType.CONTINUE and not self._options.continue_ok)
                    ):
                        return self.emit(TokenType.IDENTIFIER)
                    return self.emit(item)
                elif word[0] == '.':
                    return self.emit(TokenType.FIELD)
                elif word == 'true' or word == 'false':
                    return self.emit(TokenType.BOOL)
                else:
                    return self.emit(TokenType.IDENTIFIER)

    def _lex_field(self) -> StateFn:
        # _lex_field scans a field: .Alphanumeric. The . has been scanned.
        return self._lex_field_or_variable(TokenType.FIELD)

    def _lex_variable(self) -> StateFn:
        # _lex_variable scans a Variable: $Alphanumeric. The $ has been scanned.
        if self.at_terminator():  # Nothing interesting follows -> '$'.
            return self.emit(TokenType.VARIABLE)
        return self._lex_field_or_variable(TokenType.VARIABLE)

    def _lex_field_or_variable(self, typ: TokenType) -> StateFn:
        # _lex_field_or_variable scans a field or variable: [.$]Alphanumeric. The . or $ has been scanned.
        if self.at_terminator(): # Nothing interesting follows -> '.' or '$'.
            if typ == TokenType.VARIABLE:
                return self.emit(TokenType.VARIABLE)
            return self.emit(TokenType.DOT)
        r = ''
        while True:
            r = self.next()
            if not is_alpha_numeric(r):
                self.backup()
                break
        if not self.at_terminator():
            return self.error('bad character %r', r)
        return self.emit(typ)

    def at_terminator(self) -> bool:
        # at_terminator reports whether the input is at valid termination character to appear after an identifier.
        # Breaks .X.Y into two pieces. Also catches cases like '$x+2' not being acceptable without a space, in case we
        # decide one day to implement arithmetic.
        r = self.peek()
        if is_space(r):
            return True
        if r in (EOF, '.', ',', '|', ':', ')', '('):
            return True
        return self._input[self._pos:].startswith(self._right_delim)

    def _lex_char(self) -> StateFn:
        # _lex_char scans a character constant. The initial quote is already scanned. Syntax checking is done by the
        # parser.
        while True:
            r = self.next()
            if r == '\\':
                r = self.next()
                if r != EOF and r != '\n':
                    break
                return self.error('unterminated character constant')
            elif r in (EOF, '\n'):
                return self.error('unterminated character constant')
            elif r == '\'':
                break
        return self.emit(TokenType.CHAR_CONSTANT)

    def _lex_number(self) -> StateFn:
        # _lex_number scans a number: decimal, octal, hex, float, or imaginary. This isn't a perfect number scanner -
        # for instance it accepts '.' and '0x0.2' and '089' - but when it's wrong the input is invalid and the parser
        # (via strconv) will notice.
        if not self.scan_number():
            return self.error('bad number syntax: %r', self._input[self._start:self._pos])
        sign = self.peek()
        if sign == '+' or sign == '-':
            # Complex: 1+2i. No spaces, must end in 'i'.
            if not self.scan_number() or self._input[self._pos - 1] != 'i':
                return self.error('bad number syntax: %r', self._input[self._start:self._pos])
            return self.emit(TokenType.COMPLEX)
        return self.emit(TokenType.NUMBER)

    def scan_number(self) -> bool:
        # Optional leading sign.
        self.accept('+-')
        # Is it hex?
        digits = '0123456789_'
        if self.accept('0'):
            # Note: Leading 0 does not mean octal in floats.
            if self.accept('xX'):
                digits = '0123456789abcdefABCDEF_'
            elif self.accept('oO'):
                digits = '01234567_'
            elif self.accept('bB'):
                digits = '01_'
        self.accept_run(digits)
        if self.accept('.'):
            self.accept_run(digits)
        if len(digits) == 10 + 1 and self.accept('eE'):
            self.accept('+-')
            self.accept_run('0123456789_')
        if len(digits) == 16 + 6 + 1 and self.accept('pP'):
            self.accept('+-')
            self.accept_run('0123456789_')
        # Is it imaginary?
        self.accept('i')
        # Next thing mustn't be alphanumeric.
        if is_alpha_numeric(self.peek()):
            self.next()
            return False
        return True

    def _lex_quote(self) -> StateFn:
        # _lex_quote scans a quoted string.
        while True:
            r = self.next()
            if r == '\\':
                r = self.next()
                if r != EOF and r != '\n':
                    break
            elif r in (EOF, '\n'):
                return self.error('unterminated quoted string')
            elif r == '"':
                break
        return self.emit(TokenType.STRING)

    def _lex_raw_quote(self) -> StateFn:
        # _lex_raw_quote scans a raw quoted string.
        while True:
            r = self.next()
            if r == EOF:
                return self.error('unterminated raw quoted string')
            elif r == '`':
                break
        return self.emit(TokenType.RAW_STRING)


def right_trim_length(s: str) -> int:
    # right_trim_length returns the length of the spaces at the end of the string.
    return len(s) - len(s.rstrip(SPACE_CHARS))


def left_trim_length(s: str) -> int:
    # left_trim_length returns the length of the spaces at the beginning of the string.
    return len(s) - len(s.lstrip(SPACE_CHARS))


def is_space(r: str) -> bool:
    # is_space reports whether r is a space character.
    return r == ' ' or r == '\t' or r == '\r' or r == '\n'


def is_alpha_numeric(r: str) -> bool:
    # is_alpha_numeric reports whether r is an alphabetic, digit, or underscore.
    return r == '_' or r in string.ascii_letters or r in string.digits


def has_left_trim_marker(s: str) -> bool:
    return len(s) >= 2 and s[0] == TRIM_MARKER and is_space(s[1])


def has_right_trim_marker(s: str) -> bool:
    return len(s) >= 2 and is_space(s[0]) and s[1] == TRIM_MARKER


##


SRC = """
{{- range .Messages }}GPT4 Correct
{{- if eq .Role "system" }} System:
{{- else if eq .Role "user" }} User:
{{- else if eq .Role "assistant" }} Assistant:
{{- end }} {{ .Content }}<|end_of_turn|>
{{- end }}GPT4 Correct Assistant:
"""


def _main():
    pass


if __name__ == '__main__':
    _main()
