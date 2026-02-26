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
r"""
package syntax

import (
    "fmt"
    "strings"
    "unicode"
    "unicode/utf8"
)

type QuoteError struct {
    ByteOffset int
    Message    string
}

func (e QuoteError) Error() string {
    return fmt.Sprintf("cannot quote character at byte %d: %s", e.ByteOffset, e.Message)
}

const (
    quoteErrNull  = "shell strings cannot contain null bytes"
    quoteErrPOSIX = "POSIX shell lacks escape sequences"
    quoteErrRange = "rune out of range"
    quoteErrMksh  = "mksh cannot escape codepoints above 16 bits"
)

// Quote returns a quoted version of the input string,
// so that the quoted version is expanded or interpreted
// as the original string in the given language variant.
//
// Quoting is necessary when using arbitrary literal strings
// as words in a shell script or command.
// Without quoting, one can run into syntax errors,
// as well as the possibility of running unintended code.
//
// An error is returned when a string cannot be quoted for a variant.
// For instance, POSIX lacks escape sequences for non-printable characters,
// and no language variant can represent a string containing null bytes.
// In such cases, the returned error type will be *QuoteError.
//
// The quoting strategy is chosen on a best-effort basis,
// to minimize the amount of extra bytes necessary.
//
// Some strings do not require any quoting and are returned unchanged.
// Those strings can be directly surrounded in single quotes as well.
func Quote(s string, lang LangVariant) (string, error) {
    if s == "" {
        // Special case; an empty string must always be quoted,
        // as otherwise it expands to zero fields.
        return "''", nil
    }
    shellChars := false
    nonPrintable := false
    offs := 0
    for rem := s; len(rem) > 0; {
        r, size := utf8.DecodeRuneInString(rem)
        switch r {
        // Like regOps; token characters.
        case ';', '"', '\'', '(', ')', '$', '|', '&', '>', '<', '`',
            // Whitespace; might result in multiple fields.
            ' ', '\t', '\r', '\n',
            // Escape sequences would be expanded.
            '\\',
            // Would start a comment unless quoted.
            '#',
            // Might result in brace expansion.
            '{',
            // Might result in tilde expansion.
            '~',
            // Might result in globbing.
            '*', '?', '[',
            // Might result in an assignment.
            '=':
            shellChars = true
        case '\x00':
            return "", &QuoteError{ByteOffset: offs, Message: quoteErrNull}
        }
        if r == utf8.RuneError || !unicode.IsPrint(r) {
            if lang.in(LangPOSIX) {
                return "", &QuoteError{ByteOffset: offs, Message: quoteErrPOSIX}
            }
            nonPrintable = true
        }
        rem = rem[size:]
        offs += size
    }
    if !shellChars && !nonPrintable && !IsKeyword(s) {
        // Nothing to quote; avoid allocating.
        return s, nil
    }

    // Single quotes are usually best,
    // as they don't require any escaping of characters.
    // If we have any invalid utf8 or non-printable runes,
    // use $'' so that we can escape them.
    // Note that we can't use double quotes for those.
    var b strings.Builder
    if nonPrintable {
        b.WriteString("$'")
        lastRequoteIfHex := false
        offs := 0
        for rem := s; len(rem) > 0; {
            nextRequoteIfHex := false
            r, size := utf8.DecodeRuneInString(rem)
            switch {
            case r == '\'', r == '\\':
                b.WriteByte('\\')
                b.WriteRune(r)
            case unicode.IsPrint(r) && r != utf8.RuneError:
                if lastRequoteIfHex && isHex(r) {
                    b.WriteString("'$'")
                }
                b.WriteRune(r)
            case r == '\a':
                b.WriteString(`\a`)
            case r == '\b':
                b.WriteString(`\b`)
            case r == '\f':
                b.WriteString(`\f`)
            case r == '\n':
                b.WriteString(`\n`)
            case r == '\r':
                b.WriteString(`\r`)
            case r == '\t':
                b.WriteString(`\t`)
            case r == '\v':
                b.WriteString(`\v`)
            case r < utf8.RuneSelf, r == utf8.RuneError && size == 1:
                // \xXX, fixed at two hexadecimal characters.
                fmt.Fprintf(&b, "\\x%02x", rem[0])
                // Unfortunately, mksh allows \x to consume more hex characters.
                // Ensure that we don't allow it to read more than two.
                if lang.in(LangMirBSDKorn) {
                    nextRequoteIfHex = true
                }
            case r > utf8.MaxRune:
                // Not a valid Unicode code point?
                return "", &QuoteError{ByteOffset: offs, Message: quoteErrRange}
            case lang.in(LangMirBSDKorn) && r > 0xFFFD:
                // From the CAVEATS section in R59's man page:
                //
                // mksh currently uses OPTU-16 internally, which is the same as
                // UTF-8 and CESU-8 with 0000..FFFD being valid codepoints.
                return "", &QuoteError{ByteOffset: offs, Message: quoteErrMksh}
            case r < 0x10000:
                // \uXXXX, fixed at four hexadecimal characters.
                fmt.Fprintf(&b, "\\u%04x", r)
            default:
                // \UXXXXXXXX, fixed at eight hexadecimal characters.
                fmt.Fprintf(&b, "\\U%08x", r)
            }
            rem = rem[size:]
            lastRequoteIfHex = nextRequoteIfHex
            offs += size
        }
        b.WriteString("'")
        return b.String(), nil
    }

    // Single quotes without any need for escaping.
    if !strings.Contains(s, "'") {
        return "'" + s + "'", nil
    }

    // The string contains single quotes,
    // so fall back to double quotes.
    b.WriteByte('"')
    for _, r := range s {
        switch r {
        case '"', '\\', '`', '$':
            b.WriteByte('\\')
        }
        b.WriteRune(r)
    }
    b.WriteByte('"')
    return b.String(), nil
}

func isHex(r rune) bool {
    return (r >= '0' && r <= '9') ||
        (r >= 'a' && r <= 'f') || (r >= 'A' && r <= 'F')
}
"""  # noqa
