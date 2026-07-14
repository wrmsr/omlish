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

from ..dotenv import DotenvBinding
from ..dotenv import DotenvOriginal
from ..dotenv import parse_dotenv_stream


@pytest.mark.parametrize(('test_input', 'expected'), [
    ('', []),
    ('a=b', [DotenvBinding(key='a', value='b', original=DotenvOriginal(string='a=b', line=1), error=False)]),
    ("'a'=b", [DotenvBinding(key='a', value='b', original=DotenvOriginal(string="'a'=b", line=1), error=False)]),
    ('[=b', [DotenvBinding(key='[', value='b', original=DotenvOriginal(string='[=b', line=1), error=False)]),
    (' a = b ', [DotenvBinding(key='a', value='b', original=DotenvOriginal(string=' a = b ', line=1), error=False)]),
    ('export a=b', [DotenvBinding(key='a', value='b', original=DotenvOriginal(string='export a=b', line=1), error=False)]),  # noqa
    (
        " export 'a'=b",
        [DotenvBinding(key='a', value='b', original=DotenvOriginal(string=" export 'a'=b", line=1), error=False)],
    ),
    ('# a=b', [DotenvBinding(key=None, value=None, original=DotenvOriginal(string='# a=b', line=1), error=False)]),
    ('a=b#c', [DotenvBinding(key='a', value='b#c', original=DotenvOriginal(string='a=b#c', line=1), error=False)]),
    (
        'a=b #c',
        [DotenvBinding(key='a', value='b', original=DotenvOriginal(string='a=b #c', line=1), error=False)],
    ),
    (
        'a=b\t#c',
        [DotenvBinding(key='a', value='b', original=DotenvOriginal(string='a=b\t#c', line=1), error=False)],
    ),
    (
        'a=b c',
        [DotenvBinding(key='a', value='b c', original=DotenvOriginal(string='a=b c', line=1), error=False)],
    ),
    (
        'a=b\tc',
        [DotenvBinding(key='a', value='b\tc', original=DotenvOriginal(string='a=b\tc', line=1), error=False)],
    ),
    (
        'a=b  c',
        [DotenvBinding(key='a', value='b  c', original=DotenvOriginal(string='a=b  c', line=1), error=False)],
    ),
    (
        'a=b\u00a0 c',
        [DotenvBinding(key='a', value='b\u00a0 c', original=DotenvOriginal(string='a=b\u00a0 c', line=1), error=False)],
    ),
    (
        'a=b c ',
        [DotenvBinding(key='a', value='b c', original=DotenvOriginal(string='a=b c ', line=1), error=False)],
    ),
    (
        "a='b c '",
        [DotenvBinding(key='a', value='b c ', original=DotenvOriginal(string="a='b c '", line=1), error=False)],
    ),
    (
        'a="b c "',
        [DotenvBinding(key='a', value='b c ', original=DotenvOriginal(string='a="b c "', line=1), error=False)],
    ),
    (
        'export export_a=1',
        [DotenvBinding(key='export_a', value='1', original=DotenvOriginal(string='export export_a=1', line=1), error=False)],  # noqa
    ),
    (
        'export port=8000',
        [DotenvBinding(key='port', value='8000', original=DotenvOriginal(string='export port=8000', line=1), error=False)],  # noqa
    ),
    ('a="b\nc"', [DotenvBinding(key='a', value='b\nc', original=DotenvOriginal(string='a="b\nc"', line=1), error=False)]),  # noqa
    ("a='b\nc'", [DotenvBinding(key='a', value='b\nc', original=DotenvOriginal(string="a='b\nc'", line=1), error=False)]),  # noqa
    ('a="b\\nc"', [DotenvBinding(key='a', value='b\nc', original=DotenvOriginal(string='a="b\\nc"', line=1), error=False)]),  # noqa
    ("a='b\\nc'", [DotenvBinding(key='a', value='b\\nc', original=DotenvOriginal(string="a='b\\nc'", line=1), error=False)]),  # noqa
    ('a="b\\"c"', [DotenvBinding(key='a', value='b"c', original=DotenvOriginal(string='a="b\\"c"', line=1), error=False)]),  # noqa
    ("a='b\\'c'", [DotenvBinding(key='a', value="b'c", original=DotenvOriginal(string="a='b\\'c'", line=1), error=False)]),  # noqa
    ('a=à', [DotenvBinding(key='a', value='à', original=DotenvOriginal(string='a=à', line=1), error=False)]),
    ('a="à"', [DotenvBinding(key='a', value='à', original=DotenvOriginal(string='a="à"', line=1), error=False)]),
    (
        'no_value_var',
        [DotenvBinding(key='no_value_var', value=None, original=DotenvOriginal(string='no_value_var', line=1), error=False)],  # noqa
    ),
    ('a: b', [DotenvBinding(key=None, value=None, original=DotenvOriginal(string='a: b', line=1), error=True)]),
    (
        'a=b\nc=d',
        [
            DotenvBinding(key='a', value='b', original=DotenvOriginal(string='a=b\n', line=1), error=False),
            DotenvBinding(key='c', value='d', original=DotenvOriginal(string='c=d', line=2), error=False),
        ],
    ),
    (
        'a=b\rc=d',
        [
            DotenvBinding(key='a', value='b', original=DotenvOriginal(string='a=b\r', line=1), error=False),
            DotenvBinding(key='c', value='d', original=DotenvOriginal(string='c=d', line=2), error=False),
        ],
    ),
    (
        'a=b\r\nc=d',
        [
            DotenvBinding(key='a', value='b', original=DotenvOriginal(string='a=b\r\n', line=1), error=False),
            DotenvBinding(key='c', value='d', original=DotenvOriginal(string='c=d', line=2), error=False),
        ],
    ),
    (
        'a=\nb=c',
        [
            DotenvBinding(key='a', value='', original=DotenvOriginal(string='a=\n', line=1), error=False),
            DotenvBinding(key='b', value='c', original=DotenvOriginal(string='b=c', line=2), error=False),
        ],
    ),
    (
        '\n\n',
        [
            DotenvBinding(key=None, value=None, original=DotenvOriginal(string='\n\n', line=1), error=False),
        ],
    ),
    (
        'a=b\n\n',
        [
            DotenvBinding(key='a', value='b', original=DotenvOriginal(string='a=b\n', line=1), error=False),
            DotenvBinding(key=None, value=None, original=DotenvOriginal(string='\n', line=2), error=False),
        ],
    ),
    (
        'a=b\n\nc=d',
        [
            DotenvBinding(key='a', value='b', original=DotenvOriginal(string='a=b\n', line=1), error=False),
            DotenvBinding(key='c', value='d', original=DotenvOriginal(string='\nc=d', line=2), error=False),
        ],
    ),
    (
        'a="\nb=c',
        [
            DotenvBinding(key=None, value=None, original=DotenvOriginal(string='a="\n', line=1), error=True),
            DotenvBinding(key='b', value='c', original=DotenvOriginal(string='b=c', line=2), error=False),
        ],
    ),
    (
        '# comment\na="b\nc"\nd=e\n',
        [
            DotenvBinding(key=None, value=None, original=DotenvOriginal(string='# comment\n', line=1), error=False),
            DotenvBinding(key='a', value='b\nc', original=DotenvOriginal(string='a="b\nc"\n', line=2), error=False),
            DotenvBinding(key='d', value='e', original=DotenvOriginal(string='d=e\n', line=4), error=False),
        ],
    ),
    (
        'a=b\n# comment 1',
        [
            DotenvBinding(key='a', value='b', original=DotenvOriginal(string='a=b\n', line=1), error=False),
            DotenvBinding(key=None, value=None, original=DotenvOriginal(string='# comment 1', line=2), error=False),
        ],
    ),
    (
        '# comment 1\n# comment 2',
        [
            DotenvBinding(key=None, value=None, original=DotenvOriginal(string='# comment 1\n', line=1), error=False),
            DotenvBinding(key=None, value=None, original=DotenvOriginal(string='# comment 2', line=2), error=False),
        ],
    ),
    (
        'uglyKey[%$="S3cr3t_P4ssw#rD" #\na=b',
        [
            DotenvBinding(
                key='uglyKey[%$',
                value='S3cr3t_P4ssw#rD',
                original=DotenvOriginal(string='uglyKey[%$="S3cr3t_P4ssw#rD" #\n', line=1),
                error=False,
            ),
            DotenvBinding(key='a', value='b', original=DotenvOriginal(string='a=b', line=2), error=False),
        ],
    ),
])
def test_parse_stream(test_input, expected):
    result = parse_dotenv_stream(io.StringIO(test_input))

    assert list(result) == expected
