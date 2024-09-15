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
