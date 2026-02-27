# Copyright (c) 2016, Daniel Martí. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided with the distribution.
# * Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#   products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from omlish import dataclasses as dc

from .errors import Error


##


@dc.dataclass()
class QuoteError(Error):
    byte_offset: int
    s: str
    
    @property
    def message(self) -> str:
        return f'cannot quote character at byte {self.byte_offset}: {self.s}'


QUOTE_ERR_NULL  = 'shell strings cannot contain null bytes'
QUOTE_ERR_POSIX = 'POSIX shell lacks escape sequences'
QUOTE_ERR_RANGE = 'rune out of range'
QUOTE_ERR_MKSH  = 'mksh cannot escape codepoints above 16 bits'


# Quote returns a quoted version of the input string,
# so that the quoted version is expanded or interpreted
# as the original string in the given language variant.
#
# Quoting is necessary when using arbitrary literal strings
# as words in a shell script or command.
# Without quoting, one can run into syntax errors,
# as well as the possibility of running unintended code.
#
# An error is returned when a string cannot be quoted for a variant.
# For instance, POSIX lacks escape sequences for non-printable characters,
# and no language variant can represent a string containing null bytes.
# In such cases, the returned error type will be *QuoteError.
#
# The quoting strategy is chosen on a best-effort basis,
# to minimize the amount of extra bytes necessary.
#
# Some strings do not require any quoting and are returned unchanged.
# Those strings can be directly surrounded in single quotes as well.
def quote(s: str, lng: LangVariant) -> str | Error:
    if not s:
        # Special case; an empty string must always be quoted,
        # as otherwise it expands to zero fields.
        return "''"
        
    shell_chars = False
    non_printable = False
    offs = 0
    
    rem = s
    while len(rem) > 0:
        r, size = utf8.DecodeRuneInString(rem)
        # Like regOps; token characters.
        if r in (
            ';', '"', '\'', '(', ')', '$', '|', '&', '>', '<', '`',
            # Whitespace; might result in multiple fields.
            ' ', '\t', '\r', '\n',
            # Escape sequences would be expanded.
            '\\',
            # Would start a comment unless quoted.
            '#',
            # Might result in brace expansion.
            '{',
            # Might result in tilde expansion.
            '~',
            # Might result in globbing.
            '*', '?', '[',
            # Might result in an assignment.
            '='
        ):
            shell_chars = True
        elif r == '\x00':
            return QuoteError(offs, QUOTE_ERR_NULL)
        if r == utf8.RuneError or not unicode.IsPrint(r):
            if lng.in_(LangPOSIX):
                return QuoteError(offs, QUOTE_ERR_POSIX)
            non_printable = True
        rem = rem[size:]
        offs += size
        
    if not shell_chars and not non_printable and not is_keyword(s)
        # Nothing to quote; avoid allocating.
        return s

    # Single quotes are usually best,
    # as they don't require any escaping of characters.
    # If we have any invalid utf8 or non-printable runes,
    # use $'' so that we can escape them.
    # Note that we can't use double quotes for those.
    b = io.StringIO()
    if non_printable:
        b.write("$'")
        last_requote_if_hex = False
        offs = 0
        rem = s
        while len(rem) > 0:
            next_requote_if_hex = False
            r, size = utf8.DecodeRuneInString(rem)
            if r == '\'' or r == '\\':
                b.write('\\')
                b.write(r)
            elif unicode.IsPrint(r) and r != utf8.RuneError:
                if last_requote_if_hex and is_hex(r):
                    b.write("'$'")
                b.write(r)
            elif r == '\a':
                b.write('\\a')
            elif r == '\b':
                b.write('\\b')
            elif r == '\f':
                b.write('\\f')
            elif r == '\n':
                b.write('\\n')
            elif r == '\r':
                b.write('\\r')
            elif r == '\t':
                b.write('\\t')
            elif r == '\v':
                b.write('\\v')
            elif r < utf8.RuneSelf or (r == utf8.RuneError and size == 1):
                # \xXX, fixed at two hexadecimal characters.
                b.write("\\x%02x" % (rem[0],))
                # Unfortunately, mksh allows \x to consume more hex characters.
                # Ensure that we don't allow it to read more than two.
                if lng.in_(LangMirBSDKorn):
                    next_requote_if_hex = True
            elif r > utf8.MaxRune:
                # Not a valid Unicode code point?
                return QuoteError(offs, QUOTE_ERR_RANGE)
            elif lng.in_(LangMirBSDKorn) and r > 0xFFFD:
                # From the CAVEATS section in R59's man page:
                #
                # mksh currently uses OPTU-16 internally, which is the same as
                # UTF-8 and CESU-8 with 0000..FFFD being valid codepoints.
                return QuoteError(offs, QUOTE_ERR_MKSH)
            elif r < 0x10000:
                # \uXXXX, fixed at four hexadecimal characters.
                b.write("\\u%04x" % (r,))
            else:
                # \UXXXXXXXX, fixed at eight hexadecimal characters.
                b.write("\\U%08x" % (r,))
            rem = rem[size:]
            last_requote_if_hex = next_requote_if_hex
            offs += size

        b.write("'")
        return b.getvalue()

    # Single quotes without any need for escaping.
    if "'" not in s:
        return "'" + s + "'"

    # The string contains single quotes,
    # so fall back to double quotes.
    b.write('"')
    for r in s:
        if r in ('"', '\\', '`', '$'):
            b.write('\\')
        b.write(r)
    b.write('"')
    return b.getvalue()


def is_hex(r: str) -> bool:
    return ('0' <= r <= '9') or ('a' <= r <= 'f') or ('A' <= r <= 'F')
