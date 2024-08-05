# Copyright (c) 2014, Saurabh Kumar (python-dotenv), 2013, Ted Tieken (django-dotenv-rw), 2013, Jacob Kaplan-Moss
# (django-dotenv)
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided with the distribution.
#
# - Neither the name of django-dotenv nor the names of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import io

import pytest

from ..dotenv import Binding
from ..dotenv import Original
from ..dotenv import parse_stream


@pytest.mark.parametrize(('test_input', 'expected'), [
    ('', []),
    ('a=b', [Binding(key='a', value='b', original=Original(string='a=b', line=1), error=False)]),
    ("'a'=b", [Binding(key='a', value='b', original=Original(string="'a'=b", line=1), error=False)]),
    ('[=b', [Binding(key='[', value='b', original=Original(string='[=b', line=1), error=False)]),
    (' a = b ', [Binding(key='a', value='b', original=Original(string=' a = b ', line=1), error=False)]),
    ('export a=b', [Binding(key='a', value='b', original=Original(string='export a=b', line=1), error=False)]),
    (
        " export 'a'=b",
        [Binding(key='a', value='b', original=Original(string=" export 'a'=b", line=1), error=False)],
    ),
    ('# a=b', [Binding(key=None, value=None, original=Original(string='# a=b', line=1), error=False)]),
    ('a=b#c', [Binding(key='a', value='b#c', original=Original(string='a=b#c', line=1), error=False)]),
    (
        'a=b #c',
        [Binding(key='a', value='b', original=Original(string='a=b #c', line=1), error=False)],
    ),
    (
        'a=b\t#c',
        [Binding(key='a', value='b', original=Original(string='a=b\t#c', line=1), error=False)],
    ),
    (
        'a=b c',
        [Binding(key='a', value='b c', original=Original(string='a=b c', line=1), error=False)],
    ),
    (
        'a=b\tc',
        [Binding(key='a', value='b\tc', original=Original(string='a=b\tc', line=1), error=False)],
    ),
    (
        'a=b  c',
        [Binding(key='a', value='b  c', original=Original(string='a=b  c', line=1), error=False)],
    ),
    (
        'a=b\u00a0 c',
        [Binding(key='a', value='b\u00a0 c', original=Original(string='a=b\u00a0 c', line=1), error=False)],
    ),
    (
        'a=b c ',
        [Binding(key='a', value='b c', original=Original(string='a=b c ', line=1), error=False)],
    ),
    (
        "a='b c '",
        [Binding(key='a', value='b c ', original=Original(string="a='b c '", line=1), error=False)],
    ),
    (
        'a="b c "',
        [Binding(key='a', value='b c ', original=Original(string='a="b c "', line=1), error=False)],
    ),
    (
        'export export_a=1',
        [Binding(key='export_a', value='1', original=Original(string='export export_a=1', line=1), error=False)],
    ),
    (
        'export port=8000',
        [Binding(key='port', value='8000', original=Original(string='export port=8000', line=1), error=False)],
    ),
    ('a="b\nc"', [Binding(key='a', value='b\nc', original=Original(string='a="b\nc"', line=1), error=False)]),
    ("a='b\nc'", [Binding(key='a', value='b\nc', original=Original(string="a='b\nc'", line=1), error=False)]),
    ('a="b\\nc"', [Binding(key='a', value='b\nc', original=Original(string='a="b\\nc"', line=1), error=False)]),
    ("a='b\\nc'", [Binding(key='a', value='b\\nc', original=Original(string="a='b\\nc'", line=1), error=False)]),
    ('a="b\\"c"', [Binding(key='a', value='b"c', original=Original(string='a="b\\"c"', line=1), error=False)]),
    ("a='b\\'c'", [Binding(key='a', value="b'c", original=Original(string="a='b\\'c'", line=1), error=False)]),
    ('a=à', [Binding(key='a', value='à', original=Original(string='a=à', line=1), error=False)]),
    ('a="à"', [Binding(key='a', value='à', original=Original(string='a="à"', line=1), error=False)]),
    (
        'no_value_var',
        [Binding(key='no_value_var', value=None, original=Original(string='no_value_var', line=1), error=False)],
    ),
    ('a: b', [Binding(key=None, value=None, original=Original(string='a: b', line=1), error=True)]),
    (
        'a=b\nc=d',
        [
            Binding(key='a', value='b', original=Original(string='a=b\n', line=1), error=False),
            Binding(key='c', value='d', original=Original(string='c=d', line=2), error=False),
        ],
    ),
    (
        'a=b\rc=d',
        [
            Binding(key='a', value='b', original=Original(string='a=b\r', line=1), error=False),
            Binding(key='c', value='d', original=Original(string='c=d', line=2), error=False),
        ],
    ),
    (
        'a=b\r\nc=d',
        [
            Binding(key='a', value='b', original=Original(string='a=b\r\n', line=1), error=False),
            Binding(key='c', value='d', original=Original(string='c=d', line=2), error=False),
        ],
    ),
    (
        'a=\nb=c',
        [
            Binding(key='a', value='', original=Original(string='a=\n', line=1), error=False),
            Binding(key='b', value='c', original=Original(string='b=c', line=2), error=False),
        ],
    ),
    (
        '\n\n',
        [
            Binding(key=None, value=None, original=Original(string='\n\n', line=1), error=False),
        ],
    ),
    (
        'a=b\n\n',
        [
            Binding(key='a', value='b', original=Original(string='a=b\n', line=1), error=False),
            Binding(key=None, value=None, original=Original(string='\n', line=2), error=False),
        ],
    ),
    (
        'a=b\n\nc=d',
        [
            Binding(key='a', value='b', original=Original(string='a=b\n', line=1), error=False),
            Binding(key='c', value='d', original=Original(string='\nc=d', line=2), error=False),
        ],
    ),
    (
        'a="\nb=c',
        [
            Binding(key=None, value=None, original=Original(string='a="\n', line=1), error=True),
            Binding(key='b', value='c', original=Original(string='b=c', line=2), error=False),
        ],
    ),
    (
        '# comment\na="b\nc"\nd=e\n',
        [
            Binding(key=None, value=None, original=Original(string='# comment\n', line=1), error=False),
            Binding(key='a', value='b\nc', original=Original(string='a="b\nc"\n', line=2), error=False),
            Binding(key='d', value='e', original=Original(string='d=e\n', line=4), error=False),
        ],
    ),
    (
        'a=b\n# comment 1',
        [
            Binding(key='a', value='b', original=Original(string='a=b\n', line=1), error=False),
            Binding(key=None, value=None, original=Original(string='# comment 1', line=2), error=False),
        ],
    ),
    (
        '# comment 1\n# comment 2',
        [
            Binding(key=None, value=None, original=Original(string='# comment 1\n', line=1), error=False),
            Binding(key=None, value=None, original=Original(string='# comment 2', line=2), error=False),
        ],
    ),
    (
        'uglyKey[%$="S3cr3t_P4ssw#rD" #\na=b',
        [
            Binding(
                key='uglyKey[%$',
                value='S3cr3t_P4ssw#rD',
                original=Original(string='uglyKey[%$="S3cr3t_P4ssw#rD" #\n', line=1),
                error=False,
            ),
            Binding(key='a', value='b', original=Original(string='a=b', line=2), error=False),
        ],
    ),
])
def test_parse_stream(test_input, expected):
    result = parse_stream(io.StringIO(test_input))

    assert list(result) == expected
