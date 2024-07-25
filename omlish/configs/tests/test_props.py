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
import io

import pytest

from ..props import ParseError
from ..props import Properties


def test_basic_equals_sign():
    p = Properties()
    p.load('Truth = Beauty\n')
    assert p.properties == {'Truth': 'Beauty'}


def test_basic_colon_and_leading_whitespace():
    p = Properties()
    p.load('  Truth:Beauty')
    assert p.properties == {'Truth': 'Beauty'}


def test_basic_key_trailing_space():
    p = Properties()
    p.load('Truth                    :Beauty')
    assert p.properties == {'Truth': 'Beauty'}


def test_basic_whitespace():
    p = Properties()
    p.load("""fruits            apple, banana, pear, \\
                                cantaloupe, watermelon, \\
                                kiwi, mango""")

    assert p.properties == {'fruits': 'apple, banana, pear, cantaloupe, watermelon, kiwi, mango'}


def test_basic_key_only():
    p = Properties()
    p.load('cheese\n')

    assert p.properties == {'cheese': ''}


def test_basic_escape_write():
    p = Properties()
    p['key'] = 'hello\nworld'

    out = io.BytesIO()
    p.store(out, timestamp=None)

    out.seek(0)
    assert out.read() == b'key=hello\\nworld\n'


def test_simple_escape_parsing():
    p = Properties()
    p.load(io.BytesIO(
        b'key value with a\\ttab\n'
        b'foo ba\\r\n'
        b'new li\\ne\n'
        b'form \\feed seen!',
    ))

    assert p.properties == {'key': 'value with a\ttab', 'foo': 'ba\r', 'new': 'li\ne', 'form': '\feed seen!'}


def test_line_continuation_allowed():
    p = Properties()
    p.load(io.BytesIO(br"""
        multi\
        line\ key = value
    """))

    assert p.properties == {'multiline key': 'value'}


def test_line_continuation_forbidden():
    # In metadata comments, line continuation is disabled.

    p = Properties()
    p.load(io.BytesIO(br"""
        #: metakey meta\
        value continuation

        multi\
        line\ key = value
    """))

    assert p.properties == {'multiline key': 'value', 'value': 'continuation'}


def test_stray_line_continuation():
    p = Properties()
    p.load(io.BytesIO(b'key value\\'))

    assert p.properties == {'key': 'value'}


def test_nokey():
    p = Properties()
    p.load(b'= no key!')

    assert p.properties == {'': 'no key!'}
    assert p[''] == ('no key!', {})


def test_nokey_repeated():
    p = Properties()
    p.load(b'= no key!\n: still no key!')

    assert p.properties == {'': 'still no key!'}
    assert p[''] == ('still no key!', {})


def test_novalue():
    p = Properties()
    p.load(br'no\ value!')

    assert p.properties == {'no value!': ''}


def test_repeated():
    p = Properties()
    p.load(b'key:value\nkey=the value\nkey = value1\nkey : value2\nkey value3\nkey\tvalue4')

    assert p.properties == {'key': 'value4'}


def test_repeated_with_meta():
    p = Properties()
    p.load(b"""
        key = value1

        #: metakey = metaval1
        #: metakey2 = metaval22
        key = value2

        # Expected: Metadata should ONLY contain the following
        # 'metakey' key.
        #: metakey = metaval2
        key = value3
    """)

    assert p.properties == {'key': 'value3'}
    assert p['key'] == ('value3', {'metakey': 'metaval2'})


def test_setmeta_bytes():
    p = Properties()
    p['a key'] = 'the value', {b'metakey': b'metaval', b'__internal': b'foo'}

    out = io.BytesIO()
    p.store(out, strip_meta=False, timestamp=False)

    out.seek(0)
    assert out.read() == b'#: metakey=metaval\na\\ key=the value\n'


def test_setmeta_unicode():
    p = Properties()
    p['a key'] = 'the value', {'metakey': 'ünicode metävalue!', '__internal': 'foo'}

    out = io.BytesIO()
    p.store(out, encoding='utf-8', strip_meta=False, timestamp=False)

    out.seek(0)
    text = '#: metakey=ünicode metävalue\\!\na\\ key=the value\n'.encode()
    assert out.read() == text


def test_setmeta_int():
    p = Properties()
    p['a key'] = 'the value', {'metakey': 42}

    out = io.BytesIO()
    p.store(out, strip_meta=False, timestamp=False)

    out.seek(0)
    assert out.read() == b'#: metakey=42\na\\ key=the value\n'


@pytest.mark.parametrize('out_encoding', ['ascii', 'latin-1'])
def test_surrogate_roundtrip(out_encoding):
    p = Properties()
    p['surrogate'] = 'Muuusic \U0001D160'

    out = io.BytesIO()
    p.store(out, encoding=out_encoding, timestamp=None)

    out.seek(0)
    dumped = out.read()
    assert dumped == b'surrogate=Muuusic \\ud834\\udd60\n'

    p2 = Properties()
    p2.load(dumped, out_encoding)

    assert p2['surrogate'] == ('Muuusic \U0001D160', {})


def test_surrogate_roundtrip_utf8():
    p = Properties()
    p['surrogate'] = 'Muuusic \U0001D160'

    out = io.BytesIO()
    p.store(out, encoding='utf-8', timestamp=None)

    out.seek(0)
    dumped = out.read()
    assert dumped == b'surrogate=Muuusic \xF0\x9D\x85\xA0\n'

    p2 = Properties()
    p2.load(dumped, 'utf-8')

    assert p2['surrogate'] == ('Muuusic \U0001D160', {})


def test_surrogate_high_without_low__garbage():
    p = Properties()

    with pytest.raises(ParseError) as excinfo:
        p.load(io.BytesIO(b'surrogate=Muuusic \\ud834 foobar\n'))

    # Caused by garbage after the first unicode escape
    assert 'High surrogate unicode escape sequence not followed by' in str(excinfo.value)


def test_surrogate_high_without_low__eof():
    p = Properties()

    with pytest.raises(ParseError) as excinfo:
        p.load(io.BytesIO(b'surrogate=Muuusic \\ud834\n'))

    # Caused by short read (read 1 byte, wanted 6) after the first unicode escape
    assert 'High surrogate unicode escape sequence not followed by' in str(excinfo.value)


def test_surrogate_high_followed_by_non_low_surrogate_uniescape():
    p = Properties()

    with pytest.raises(ParseError) as excinfo:
        p.load(io.BytesIO(b'surrogate=Muuusic \\ud834\\u000a\n'))

    # Caused by short read (read 1 byte, wanted 6) after the first unicode escape
    assert (
        'Low surrogate unicode escape sequence expected after high surrogate escape sequence, but got '
        'a non-low-surrogate unicode escape sequence'
    ) in str(excinfo.value)
