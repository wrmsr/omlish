# jProperties - Java Property file parser and writer for Python
#
# Copyright (c) 2015, Tilman Blumenbach
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided with the distribution.
#
# * Neither the name of jProperties nor the names of its contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import codecs
import collections.abc
import contextlib
import functools
import io
import itertools
import re
import struct
import sys
import time
import typing as ta


class PropertyTuple(ta.NamedTuple):
    data: ta.Any
    meta: ta.Any


def _is_runtime_meta(key: str | bytes) -> bool:
    return (
        (isinstance(key, str) and key.startswith('__')) or
        (isinstance(key, bytes) and key.startswith(b'__'))
    )


def _escape_non_ascii(unicode_obj: str | bytes) -> str:
    def replace(match):
        s = match.group(0)
        n = ord(s)
        if n < 0x10000:
            return f'\\u{n:04x}'
        else:
            n -= 0x10000
            s1 = 0xd800 | ((n >> 10) & 0x3ff)
            s2 = 0xdc00 | (n & 0x3ff)
            return f'\\u{s1:04x}\\u{s2:04x}'

    if isinstance(unicode_obj, bytes):
        unicode_obj = unicode_obj.decode('utf-8')

    return re.sub(r'[^ -~]', replace, unicode_obj)


_jbackslash_replace_codec_name = __name__ + '.jbackslashreplace'


@functools.partial(codecs.register_error, _jbackslash_replace_codec_name)
def _jbackslashreplace_error_handler(err):
    if not isinstance(err, UnicodeEncodeError):
        raise err

    return _escape_non_ascii(err.object[err.start:err.end]), err.end


def _escape_str(
        raw_str: ta.Any,
        *,
        only_leading_spaces: bool = False,
        escape_non_printing: bool = False,
        line_breaks_only: bool = False,
) -> str:
    if isinstance(raw_str, bytes):
        raw_str = raw_str.decode('utf-8')
    elif not isinstance(raw_str, str):
        raw_str = str(raw_str)

    trans_dict = {
        ord('\r'): '\\r',
        ord('\n'): '\\n',
        ord('\f'): '\\f',
    }

    if not line_breaks_only:
        trans_dict.update(
            {
                ord('#'): '\\#',
                ord('!'): '\\!',
                ord('='): '\\=',
                ord(':'): '\\:',
                ord('\\'): '\\\\',
                ord('\t'): '\\t',
            },
        )

    escaped_str = raw_str.translate(trans_dict)

    if not only_leading_spaces:
        escaped_str = escaped_str.replace(' ', '\\ ')
    else:
        escaped_str = re.sub('^ ', '\\\\ ', escaped_str)

    if escape_non_printing:
        escaped_str = _escape_non_ascii(escaped_str)

    return escaped_str


class PropertyError(Exception):
    """Base exception class for all exceptions raised by this module."""


class ParseError(PropertyError):
    def __init__(self, message: str, line_number: int, file_obj: ta.Any = None) -> None:
        super().__init__()
        self.message = message
        self.line_number = line_number
        self.file_obj = file_obj

    def __str__(self) -> str:
        filename = '<unknown>' if not hasattr(self.file_obj, 'filename') else self.file_obj.filename
        return f'Parse error in {filename}:{self.line_number}: {self.message}'


class Properties(collections.abc.MutableMapping):
    """
    A parser for Java property files.

    This class implements parsing Java property files as defined here:
    http://docs.oracle.com/javase/7/docs/api/java/util/Properties.html#load(java.io.Reader)
    """

    _EOL = '\r\n'
    _WHITESPACE = ' \t\f'
    _ALLWHITESPACE = _EOL + _WHITESPACE

    def __init__(
            self,
            *,
            process_escapes_in_values: bool = True,
    ) -> None:
        super().__init__()

        self._process_escapes_in_values = process_escapes_in_values

        self.reset()
        self.clear()

    _source_file: ta.IO[str] | None
    _next_metadata: dict[str, str]
    _lookahead: str | None = None
    _prev_key: str | None
    _metadata: dict[str, ta.Any]
    _key_order: list[str]
    _properties: dict[str, ta.Any]
    _line_number: int
    _metadoc: bool

    def __len__(self) -> int:
        return len(self._properties)

    def __getitem__(self, item: str) -> PropertyTuple:
        if not isinstance(item, str):
            raise TypeError('Property keys must be of type str')

        if item not in self._properties:
            raise KeyError('Key not found')

        return PropertyTuple(
            self._properties[item],
            self._metadata.get(item, {}),
        )

    def __setitem__(self, key: str, value) -> None:
        if not isinstance(key, str):
            raise TypeError('Property keys must be of type str')

        metadata = None
        if isinstance(value, tuple):
            value, metadata = value

        if not isinstance(value, str):
            raise TypeError('Property values must be of type str')

        if metadata is not None and not isinstance(metadata, dict):
            raise TypeError('Metadata needs to be a dictionary')

        self._properties[key] = value
        if metadata is not None:
            self._metadata[key] = metadata

    def __delitem__(self, key: str) -> None:
        if not isinstance(key, str):
            raise TypeError('Property keys must be of type str')

        if key not in self._properties:
            raise KeyError('Key not found')

        # Remove the property itself.
        del self._properties[key]

        # Remove its metadata as well.
        if key in self._metadata:
            del self._metadata[key]

        # We also no longer need to remember its key order since the property does not exist anymore.
        with contextlib.suppress(ValueError):
            self._key_order.remove(key)

    def __iter__(self) -> ta.Iterator:
        return self._properties.__iter__()

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        self._properties = value

    @properties.deleter
    def properties(self):
        self._properties = {}

    def getmeta(self, key: str) -> dict:
        return self._metadata.get(key, {})

    def setmeta(self, key: str, metadata: dict):
        if not isinstance(metadata, dict):
            raise TypeError('Metadata needs to be a dictionary')

        self._metadata[key] = metadata

    def _peek(self) -> str:
        if self._lookahead is None:
            c = self._source_file.read(1)  # type: ignore
            if c == '':
                raise EOFError
            self._lookahead = c
        return self._lookahead

    def _getc(self) -> str:
        c = self._peek()
        self._lookahead = None
        return c

    def _handle_eol(self) -> None:
        c = self._peek()

        if c == '\r':
            self._line_number += 1
            self._getc()
            try:
                if self._peek() == '\n':
                    # DOS line ending. Skip it.
                    self._getc()
            except EOFError:
                pass

        elif c == '\n':
            self._line_number += 1
            self._getc()

    def _skip_whitespace(self, stop_at_eol: bool = False) -> None:
        while True:
            c = self._peek()
            if c not in self._ALLWHITESPACE:
                return

            if c in self._EOL:
                if stop_at_eol:
                    return
                self._handle_eol()

            else:
                self._getc()

    def _skip_natural_line(self) -> str:
        line = ''
        try:
            while self._peek() not in self._EOL:
                line += self._getc()
            self._handle_eol()
        except EOFError:
            pass
        return line

    def _parse_comment(self) -> None:
        self._getc()

        if self._peek() != ':':
            docstr = self._skip_natural_line()
            if self._metadoc and self._prev_key:
                prev_metadata = self._metadata.setdefault(self._prev_key, {})
                prev_metadata.setdefault('_doc', '')
                if docstr.startswith(' '):
                    docstr = docstr[1:]
                prev_metadata['_doc'] += docstr + '\n'
            return

        self._getc()

        key = self._parse_key(True)
        value = self._parse_value(True)

        if not key:
            raise ParseError('Empty key in metadata key-value pair', self._line_number, self._source_file)

        self._next_metadata[key] = value

    # \r, \n, \t or \f.
    _ESCAPED_CHARS: ta.ClassVar[ta.Mapping[str, str]] = {
        ec: eval(r"u'\%s'" % (ec,))  # noqa
        for ec in 'rntf'
    }

    def _handle_escape(self, allow_line_continuation: bool = True) -> str:
        if self._peek() == '\\':
            self._getc()

        try:
            escaped_char = self._peek()
        except EOFError:
            return ''

        if escaped_char in self._EOL:
            if allow_line_continuation:
                try:
                    self._handle_eol()
                    self._skip_whitespace(True)
                except EOFError:
                    pass

            return ''

        self._getc()

        try:
            return self._ESCAPED_CHARS[escaped_char]
        except KeyError:
            pass

        if escaped_char == 'u':
            start_linenumber = self._line_number

            try:
                codepoint_hex = ''
                for _ in range(4):
                    codepoint_hex += self._getc()

                codepoint = int(codepoint_hex, base=16)

                # See: http://unicodebook.readthedocs.io/unicode_encodings.html#utf-16-surrogate-pairs
                if 0xD800 <= codepoint <= 0xDBFF:
                    codepoint2_hex = ''
                    try:
                        for _ in range(6):
                            codepoint2_hex += self._getc()
                    except EOFError:
                        pass

                    if codepoint2_hex[:2] != r'\u' or len(codepoint2_hex) != 6:
                        raise ParseError(
                            'High surrogate unicode escape sequence not followed by another '
                            '(low surrogate) unicode escape sequence.',
                            start_linenumber,
                            self._source_file,
                        )

                    codepoint2 = int(codepoint2_hex[2:], base=16)
                    if not (0xDC00 <= codepoint2 <= 0xDFFF):
                        raise ParseError(
                            'Low surrogate unicode escape sequence expected after high surrogate '
                            'escape sequence, but got a non-low-surrogate unicode escape sequence.',
                            start_linenumber,
                            self._source_file,
                        )

                    final_codepoint = 0x10000
                    final_codepoint += (codepoint & 0x03FF) << 10
                    final_codepoint += codepoint2 & 0x03FF

                    codepoint = final_codepoint

                return struct.pack('=I', codepoint).decode('utf-32')
            except (EOFError, ValueError) as e:
                raise ParseError('Parse error', start_linenumber, self._source_file) from e

        return escaped_char

    def _parse_key(self, single_line_only: bool = False) -> str:
        self._skip_whitespace(single_line_only)

        key = ''
        while True:
            try:
                c = self._peek()
            except EOFError:
                break

            if c == '\\':
                key += self._handle_escape(not single_line_only)
                continue

            if c in self._ALLWHITESPACE or c in ':=':
                break

            key += self._getc()

        return key

    def _parse_value(self, single_line_only: bool = False) -> str:
        try:
            self._skip_whitespace(True)
            if self._peek() in ':=':
                self._getc()
            self._skip_whitespace(True)
        except EOFError:
            return ''

        value = ''
        while True:
            try:
                c = self._peek()
            except EOFError:
                break

            if c == '\\' and self._process_escapes_in_values:
                value += self._handle_escape(not single_line_only)
                continue

            if c in self._EOL:
                self._handle_eol()
                break

            value += self._getc()

        return value

    def _parse_logical_line(self) -> bool:
        try:
            self._skip_whitespace()
            c = self._peek()
        except EOFError:
            return False

        if c in '!#':
            try:
                self._parse_comment()
            except EOFError:
                # Nothing more to parse.
                return False

            return True

        try:
            key = self._parse_key()
            value = self._parse_value()
        except EOFError:
            return False

        if key not in self._properties:
            self._key_order.append(key)

        self._properties[key] = value

        if self._next_metadata:
            self._metadata[key] = self._next_metadata
            self._next_metadata = {}
        self._prev_key = key

        return True

    def _parse(self) -> None:
        while self._parse_logical_line():
            pass

    def reset(self, metadoc: bool = False) -> None:
        self._source_file = None
        self._line_number = 1
        self._lookahead = None

        self._next_metadata = {}

        self._prev_key = None
        self._metadoc = metadoc

    def clear(self) -> None:
        self._properties = {}
        self._metadata = {}
        self._key_order = []

    def load(
            self,
            source_data,
            encoding: str | None = 'iso-8859-1',
            metadoc: bool = False,
    ) -> ta.Self:
        self.reset(metadoc)

        if isinstance(source_data, bytes):
            self._source_file = io.StringIO(source_data.decode(encoding or 'iso-8859-1'))
        elif isinstance(source_data, str):
            self._source_file = io.StringIO(source_data)
        elif encoding is not None:
            self._source_file = codecs.getreader(encoding)(source_data)  # type: ignore
        else:
            self._source_file = source_data

        self._parse()

        return self

    def store(
            self,
            out_stream,
            initial_comments: str | None = None,
            encoding: str = 'iso-8859-1',
            strict: bool = True,
            strip_meta: bool = True,
            timestamp: bool = True,
    ) -> ta.Self:
        out_codec_info = codecs.lookup(encoding)
        wrapped_out_stream = out_codec_info.streamwriter(out_stream, _jbackslash_replace_codec_name)
        properties_escape_nonprinting = strict and out_codec_info == codecs.lookup('latin_1')

        if initial_comments is not None:
            initial_comments = re.sub(r'(\r\n|\r)', '\n', initial_comments)
            initial_comments = re.sub(r'\n(?![#!])', '\n#', initial_comments)
            initial_comments = re.sub(r'(\n[#!]):', r'\g<1>\:', initial_comments)
            print('#' + initial_comments, file=wrapped_out_stream)

        if timestamp:
            day_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            now = time.gmtime()
            print(
                '#%s %s %02d %02d:%02d:%02d UTC %04d' % (
                    day_of_week[now.tm_wday],
                    month[now.tm_mon - 1],
                    now.tm_mday,
                    now.tm_hour,
                    now.tm_min,
                    now.tm_sec,
                    now.tm_year,
                ),
                file=wrapped_out_stream,
            )

        unordered_keys = set(self._properties)
        ordered_keys = set(self._key_order)
        unordered_keys -= ordered_keys

        unordered_keys_xs = list(unordered_keys)
        unordered_keys_xs.sort()

        for key in itertools.chain(self._key_order, unordered_keys_xs):
            if key in self._properties:
                metadata = self.getmeta(key)
                if not strip_meta and len(metadata):
                    for mkey in sorted(metadata):
                        if _is_runtime_meta(mkey):
                            continue

                        print(
                            '#: {}={}'.format(  # noqa
                                _escape_str(mkey),
                                _escape_str(metadata[mkey], only_leading_spaces=True),
                            ),
                            file=wrapped_out_stream,
                        )

                print(
                    '='.join([
                        _escape_str(
                            key,
                            escape_non_printing=properties_escape_nonprinting,
                        ),
                        _escape_str(
                            self._properties[key],
                            only_leading_spaces=True,
                            escape_non_printing=properties_escape_nonprinting,
                            line_breaks_only=not self._process_escapes_in_values,
                        ),
                    ]),
                    file=wrapped_out_stream,
                )

        return self

    def list(self, out_stream=sys.stderr) -> None:
        print('-- listing properties --', file=out_stream)
        for key in self._properties:
            msg = f'{key}={self._properties[key]}'
            print(msg, file=out_stream)
