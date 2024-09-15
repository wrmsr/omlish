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


class TokenType(enum.Enum):
    ERROR = enum.auto()          # error occurred; value is text of error
    Bool = enum.auto()           # boolean constant
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
        # for text that is skipped without calling self._next.
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

    def errorf(self, format: str, *args: ta.Any) -> StateFn | None:
        # errorf returns an error token and terminates the scan by passing back a nil pointer that will be the next
        # state, terminating self._next_token.
        self._token = Token(TokenType.ERROR, self._start, format % args, self._start_line)
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
        # lex_text scans until an opening action delimiter, "{{".
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


def right_trim_length(s: str) -> int:
    # right_trim_length returns the length of the spaces at the end of the string.
    return len(s) - len(s.rstrip(SPACE_CHARS))


def left_trim_length(s: str) -> int:
    # left_trim_length returns the length of the spaces at the beginning of the string.
    return len(s) - len(s.lstrip(SPACE_CHARS))


def is_space(r: str) -> bool:
    # isSpace reports whether r is a space character.
    return r == ' ' or r == '\t' or r == '\r' or r == '\n'


def is_alpha_numeric(r: str) -> bool:
    # is_alpha_numeric reports whether r is an alphabetic, digit, or underscore.
    return r == '_' or r in string.ascii_letters or r in string.digits


def has_left_trim_marker(s: str) -> bool:
    return len(s) >= 2 and s[0] == TRIM_MARKER and is_space(s[1])


def has_right_trim_marker(s: str) -> bool:
    return len(s) >= 2 and is_space(s[0]) and s[1] == TRIM_MARKER


"""



def (l: Lexer) atRightDelim() (delim, trimSpaces bool) {
    # atRightDelim reports whether the lexer is at a right delimiter, possibly preceded by a trim marker.
    if hasRightTrimMarker(l.input[l.pos:]) && strings.HasPrefix(l.input[l.pos+trimMarkerLen:], l.rightDelim) { // With trim marker.
        return true, true
    }
    if strings.HasPrefix(l.input[l.pos:], l.rightDelim) { // Without trim marker.
        return true, false
    }
    return false, false
}


def lexLeftDelim(l: Lexer) -> StateFn:
    # lexLeftDelim scans the left delimiter, which is known to be present, possibly with a trim marker. (The text to be trimmed has already been emitted.)
    l.pos += Pos(len(l.leftDelim))
    trimSpace := hasLeftTrimMarker(l.input[l.pos:])
    afterMarker := Pos(0)
    if trimSpace {
        afterMarker = trimMarkerLen
    }
    if strings.HasPrefix(l.input[l.pos+afterMarker:], leftComment) {
        l.pos += afterMarker
        l.ignore()
        return lexComment
    }
    i := l.thisItem(itemLeftDelim)
    l.insideAction = true
    l.pos += afterMarker
    l.ignore()
    l.parenDepth = 0
    return l.emitItem(i)
}

def lexComment(l: Lexer) -> StateFn:
    # lexComment scans a comment. The left comment marker is known to be present.
    l.pos += Pos(len(leftComment))
    x := strings.Index(l.input[l.pos:], rightComment)
    if x < 0 {
        return l.errorf("unclosed comment")
    }
    l.pos += Pos(x + len(rightComment))
    delim, trimSpace := l.atRightDelim()
    if !delim {
        return l.errorf("comment ends before closing delimiter")
    }
    i := l.thisItem(itemComment)
    if trimSpace {
        l.pos += trimMarkerLen
    }
    l.pos += Pos(len(l.rightDelim))
    if trimSpace {
        l.pos += leftTrimLength(l.input[l.pos:])
    }
    l.ignore()
    if l.options.emitComment {
        return l.emitItem(i)
    }
    return lexText
}

def lexRightDelim(l: Lexer) -> StateFn:
    # lexRightDelim scans the right delimiter, which is known to be present, possibly with a trim marker.
    _, trimSpace := l.atRightDelim()
    if trimSpace {
        l.pos += trimMarkerLen
        l.ignore()
    }
    l.pos += Pos(len(l.rightDelim))
    i := l.thisItem(itemRightDelim)
    if trimSpace {
        l.pos += leftTrimLength(l.input[l.pos:])
        l.ignore()
    }
    l.insideAction = false
    return l.emitItem(i)
}

def lexInsideAction(l: Lexer) -> StateFn:
    # lexInsideAction scans the elements inside action delimiters.
    // Either number, quoted string, or identifier.
    // Spaces separate arguments; runs of spaces turn into itemSpace.
    // Pipe symbols separate and are emitted.
    delim, _ := l.atRightDelim()
    if delim {
        if l.parenDepth == 0 {
            return lexRightDelim
        }
        return l.errorf("unclosed left paren")
    }
    switch r := l.next(); {
    case r == eof:
        return l.errorf("unclosed action")
    case isSpace(r):
        l.backup() // Put space back in case we have " -}}".
        return lexSpace
    case r == '=':
        return l.emit(itemAssign)
    case r == ':':
        if l.next() != '=' {
            return l.errorf("expected :=")
        }
        return l.emit(itemDeclare)
    case r == '|':
        return l.emit(itemPipe)
    case r == '"':
        return lexQuote
    case r == '`':
        return lexRawQuote
    case r == '$':
        return lexVariable
    case r == '\'':
        return lexChar
    case r == '.':
        // special look-ahead for ".field" so we don't break l.backup().
        if l.pos < Pos(len(l.input)) {
            r := l.input[l.pos]
            if r < '0' || '9' < r {
                return lexField
            }
        }
        fallthrough // '.' can start a number.
    case r == '+' || r == '-' || ('0' <= r && r <= '9'):
        l.backup()
        return lexNumber
    case isAlphaNumeric(r):
        l.backup()
        return lexIdentifier
    case r == '(':
        l.parenDepth++
        return l.emit(itemLeftParen)
    case r == ')':
        l.parenDepth--
        if l.parenDepth < 0 {
            return l.errorf("unexpected right paren")
        }
        return l.emit(itemRightParen)
    case r <= unicode.MaxASCII && unicode.IsPrint(r):
        return l.emit(itemChar)
    default:
        return l.errorf("unrecognized character in action: %#U", r)
    }
}

def lexSpace(l: Lexer) -> StateFn:
    # lexSpace scans a run of space characters. We have not consumed the first space, which is known to be present. Take care if there is a trim-marked right delimiter, which starts with a space.
    var r rune
    var numSpaces int
    for {
        r = l.peek()
        if !isSpace(r) {
            break
        }
        l.next()
        numSpaces++
    }
    // Be careful about a trim-marked closing delimiter, which has a minus
    // after a space. We know there is a space, so check for the '-' that might follow.
    if hasRightTrimMarker(l.input[l.pos-1:]) && strings.HasPrefix(l.input[l.pos-1+trimMarkerLen:], l.rightDelim) {
        l.backup() // Before the space.
        if numSpaces == 1 {
            return lexRightDelim // On the delim, so go right to that.
        }
    }
    return l.emit(itemSpace)
}

def lexIdentifier(l: Lexer) -> StateFn:
    # lexIdentifier scans an alphanumeric.
    for {
        switch r := l.next(); {
        case isAlphaNumeric(r):
            // absorb.
        default:
            l.backup()
            word := l.input[l.start:l.pos]
            if !l.atTerminator() {
                return l.errorf("bad character %#U", r)
            }
            switch {
            case key[word] > itemKeyword:
                item := key[word]
                if item == itemBreak && !l.options.breakOK || item == itemContinue && !l.options.continueOK {
                    return l.emit(itemIdentifier)
                }
                return l.emit(item)
            case word[0] == '.':
                return l.emit(itemField)
            case word == "true", word == "false":
                return l.emit(itemBool)
            default:
                return l.emit(itemIdentifier)
            }
        }
    }
}

def lexField(l: Lexer) -> StateFn:
    # lexField scans a field: .Alphanumeric. The . has been scanned.
    return lexFieldOrVariable(l, itemField)
}

def lexVariable(l: Lexer) -> StateFn:
    # lexVariable scans a Variable: $Alphanumeric. The $ has been scanned.
    if l.atTerminator() { // Nothing interesting follows -> "$".
        return l.emit(itemVariable)
    }
    return lexFieldOrVariable(l, itemVariable)
}

def lexFieldOrVariable(l: Lexer, typ itemType) -> StateFn:
    # lexFieldOrVariable scans a field or variable: [.$]Alphanumeric. The . or $ has been scanned.
    if l.atTerminator() { // Nothing interesting follows -> "." or "$".
        if typ == itemVariable {
            return l.emit(itemVariable)
        }
        return l.emit(itemDot)
    }
    var r rune
    for {
        r = l.next()
        if !isAlphaNumeric(r) {
            l.backup()
            break
        }
    }
    if !l.atTerminator() {
        return l.errorf("bad character %#U", r)
    }
    return l.emit(typ)
}

def (l: Lexer) atTerminator() bool {
    # atTerminator reports whether the input is at valid termination character to appear after an identifier. Breaks .X.Y into two pieces. Also catches cases like "$x+2" not being acceptable without a space, in case we decide one day to implement arithmetic.
    r := l.peek()
    if isSpace(r) {
        return true
    }
    switch r {
    case eof, '.', ',', '|', ':', ')', '(':
        return true
    }
    return strings.HasPrefix(l.input[l.pos:], l.rightDelim)
}

def lexChar(l: Lexer) -> StateFn:
    # lexChar scans a character constant. The initial quote is already scanned. Syntax checking is done by the parser.
Loop:
    for {
        switch l.next() {
        case '\\':
            if r := l.next(); r != eof && r != '\n' {
                break
            }
            fallthrough
        case eof, '\n':
            return l.errorf("unterminated character constant")
        case '\'':
            break Loop
        }
    }
    return l.emit(itemCharConstant)
}

def lexNumber(l: Lexer) -> StateFn:
    # lexNumber scans a number: decimal, octal, hex, float, or imaginary. This isn't a perfect number scanner - for instance it accepts "." and "0x0.2" and "089" - but when it's wrong the input is invalid and the parser (via strconv) will notice.
    if !l.scanNumber() {
        return l.errorf("bad number syntax: %q", l.input[l.start:l.pos])
    }
    if sign := l.peek(); sign == '+' || sign == '-' {
        // Complex: 1+2i. No spaces, must end in 'i'.
        if !l.scanNumber() || l.input[l.pos-1] != 'i' {
            return l.errorf("bad number syntax: %q", l.input[l.start:l.pos])
        }
        return l.emit(itemComplex)
    }
    return l.emit(itemNumber)
}

def (l: Lexer) scanNumber() bool {
    // Optional leading sign.
    l.accept("+-")
    // Is it hex?
    digits := "0123456789_"
    if l.accept("0") {
        // Note: Leading 0 does not mean octal in floats.
        if l.accept("xX") {
            digits = "0123456789abcdefABCDEF_"
        } else if l.accept("oO") {
            digits = "01234567_"
        } else if l.accept("bB") {
            digits = "01_"
        }
    }
    l.acceptRun(digits)
    if l.accept(".") {
        l.acceptRun(digits)
    }
    if len(digits) == 10+1 && l.accept("eE") {
        l.accept("+-")
        l.acceptRun("0123456789_")
    }
    if len(digits) == 16+6+1 && l.accept("pP") {
        l.accept("+-")
        l.acceptRun("0123456789_")
    }
    // Is it imaginary?
    l.accept("i")
    // Next thing mustn't be alphanumeric.
    if isAlphaNumeric(l.peek()) {
        l.next()
        return false
    }
    return true
}

def lexQuote(l: Lexer) -> StateFn:
    # lexQuote scans a quoted string.
Loop:
    for {
        switch l.next() {
        case '\\':
            if r := l.next(); r != eof && r != '\n' {
                break
            }
            fallthrough
        case eof, '\n':
            return l.errorf("unterminated quoted string")
        case '"':
            break Loop
        }
    }
    return l.emit(itemString)
}

def lexRawQuote(l: Lexer) -> StateFn:
    # lexRawQuote scans a raw quoted string.
Loop:
    for {
        switch l.next() {
        case eof:
            return l.errorf("unterminated raw quoted string")
        case '`':
            break Loop
        }
    }
    return l.emit(itemRawString)
}

"""


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
