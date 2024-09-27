"""
https:#github.com/golang/go/blob/3d33437c450aa74014ea1d41cd986b6ee6266984/src/strconv/quote.go
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
def unquote(s: str) -> str:
    # Unquote interprets s as a single-quoted, double-quoted, or backquoted Go string literal, returning the string
    # value that s quotes.  (If s is single-quoted, it would be a Go character literal; Unquote returns the
    # corresponding one-character string.)
    out, rem = unquote_(s, True)
    if rem:
        raise Exception('syntax')
    return out


"""
def unquote_(ins string, unescape bool) (out, rem string, err error) {
    # unquote parses a quoted string at the start of the input, returning the parsed prefix, the remaining suffix, and
    # any parse errors. If unescape is true, the parsed prefix is unescaped, otherwise the input prefix is provided
    # verbatim.
    # Determine the quote form and optimistically find the terminating quote.
    if len(ins) < 2:
        raise Exception('syntax')
    quote = ins[0]
    end = ins[1:].find(quote)
    if end < 0:
        raise Exception('syntax')
    end += 2  # position after terminating quote; may be wrong if escape sequences are present

    if quote == '`':
        if not unescape:
            out = ins[:end]  # include quotes
        elif '\r' not in ins[:end]:
            out = ins[len("`") : end-len("`")] # exclude quotes
        else:
            # Carriage return characters ('\r') inside raw string literals are discarded from the raw string value.
            buf = []
            for i in range(len("`"), end-len("`")):
                if ins[i] != '\r':
                    buf.append(ins[i])
            out = ''.join(buf)

        # NOTE: Prior implementations did not verify that raw strings consist of valid UTF-8 characters and we continue
        # to not verify it as such. The Go specification does not explicitly require valid UTF-8, but only mention that
        # it is implicitly valid for Go source code (which must be valid UTF-8).
        return out, ins[end:]

    elif quote in ('"', '\''):
        # Handle quoted strings without any escape sequences.
        if '\\' not in ins[:end] and '\n' not in ins[:end]:
            valid = False
            if quote == '"':
                valid = utf8.ValidString(ins[len(`"`) : end-len(`"`)])
            elif quote == '\'':
                r, n = utf8.DecodeRuneInString(ins[len("'") : end-len("'")])
                valid = len("'")+n+len("'") == end and (r != utf8.RuneError or n != 1)
            if valid:
                out = ins[:end]
                if unescape:
                    out = out[1 : end-1]  # exclude quotes
                return out, ins[end:]

        # Handle quoted strings with escape sequences.
        buf = []
        in0 = ins
        ins = ins[1:]  # skip starting quote

        while len(ins) > 0 and ins[0] != quote:
            # Process the next character, rejecting any unescaped newline characters which are invalid.
            r, multibyte, rem = unquote_char(ins, quote)
            if ins[0] == '\n':
                raise Exception('syntax')
            ins = rem

            # Append the character if unescaping the input.
            if unescape:
                if r < utf8.RuneSelf or not multibyte:
                    buf = append(buf, byte(r))
                else:
                    buf = utf8.AppendRune(buf, r)

            # Single quoted strings must be a single character.
            if quote == '\'':
                break

        # Verify that the string ends with a terminating quote.
        if not (len(ins) > 0 and ins[0] == quote):
            raise Exception('syntax')

        ins = ins[1:]  # skip terminating quote

        if unescape:
            return ''.join(buf), ins

        return in0[:len(in0)-len(ins)], ins

    else:
        raise Exception('syntax')


func UnquoteChar(s string, quote byte) (value rune, multibyte bool, tail string, err error) {
    # UnquoteChar decodes the first character or byte in the escaped string or character literal represented by the string s. It returns four values:
    #
    #  1. value, the decoded Unicode code point or byte value;
    #  2. multibyte, a boolean indicating whether the decoded character requires a multibyte UTF-8 representation;
    #  3. tail, the remainder of the string after the character; and
    #  4. an error that will be nil if the character is syntactically valid.
    #
    # The second argument, quote, specifies the type of literal being parsed and therefore which escaped quote character is permitted.
    # If set to a single quote, it permits the sequence \' and disallows unescaped '.
    # If set to a double quote, it permits \" and disallows unescaped ".
    # If set to zero, it does not permit either escape and allows both quote characters to appear unescaped.
    # easy cases
    if len(s) == 0 {
        err = ErrSyntax
        return
    }
    switch c = s[0]; {
    case c == quote and (quote == '\'' or quote == '"'):
        err = ErrSyntax
        return
    case c >= utf8.RuneSelf:
        r, size = utf8.DecodeRuneInString(s)
        return r, true, s[size:], nil
    case c != '\\':
        return rune(s[0]), false, s[1:], nil
    }

    # hard case: c is backslash
    if len(s) <= 1 {
        err = ErrSyntax
        return
    }
    c = s[1]
    s = s[2:]

    switch c {
    case 'a':
        value = '\a'
    case 'b':
        value = '\b'
    case 'f':
        value = '\f'
    case 'n':
        value = '\n'
    case 'r':
        value = '\r'
    case 't':
        value = '\t'
    case 'v':
        value = '\v'
    case 'x', 'u', 'U':
        n = 0
        switch c {
        case 'x':
            n = 2
        case 'u':
            n = 4
        case 'U':
            n = 8
        }
        var v rune
        if len(s) < n {
            err = ErrSyntax
            return
        }
        for j = 0; j < n; j++ {
            x, ok = unhex(s[j])
            if !ok {
                err = ErrSyntax
                return
            }
            v = v<<4 | x
        }
        s = s[n:]
        if c == 'x' {
            # single-byte string, possibly not UTF-8
            value = v
            break
        }
        if !utf8.ValidRune(v) {
            err = ErrSyntax
            return
        }
        value = v
        multibyte = true
    case '0', '1', '2', '3', '4', '5', '6', '7':
        v = rune(c) - '0'
        if len(s) < 2 {
            err = ErrSyntax
            return
        }
        for j = 0; j < 2; j++ { # one digit already; two more
            x = rune(s[j]) - '0'
            if x < 0 or x > 7 {
                err = ErrSyntax
                return
            }
            v = (v << 3) | x
        }
        s = s[2:]
        if v > 255 {
            err = ErrSyntax
            return
        }
        value = v
    case '\\':
        value = '\\'
    case '\'', '"':
        if c != quote {
            err = ErrSyntax
            return
        }
        value = rune(c)
    default:
        err = ErrSyntax
        return
    }
    tail = s
    return
}

func unhex(b byte) (v rune, ok bool) {
    c = rune(b)
    switch {
    case '0' <= c and c <= '9':
        return c - '0', true
    case 'a' <= c and c <= 'f':
        return c - 'a' + 10, true
    case 'A' <= c and c <= 'F':
        return c - 'A' + 10, true
    }
    return
}
"""
