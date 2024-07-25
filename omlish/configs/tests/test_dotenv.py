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


@pytest.mark.parametrize("test_input,expected", [
    (u"", []),
    (u"a=b", [Binding(key=u"a", value=u"b", original=Original(string=u"a=b", line=1), error=False)]),
    (u"'a'=b", [Binding(key=u"a", value=u"b", original=Original(string=u"'a'=b", line=1), error=False)]),
    (u"[=b", [Binding(key=u"[", value=u"b", original=Original(string=u"[=b", line=1), error=False)]),
    (u" a = b ", [Binding(key=u"a", value=u"b", original=Original(string=u" a = b ", line=1), error=False)]),
    (u"export a=b", [Binding(key=u"a", value=u"b", original=Original(string=u"export a=b", line=1), error=False)]),
    (
        u" export 'a'=b",
        [Binding(key=u"a", value=u"b", original=Original(string=u" export 'a'=b", line=1), error=False)],
    ),
    (u"# a=b", [Binding(key=None, value=None, original=Original(string=u"# a=b", line=1), error=False)]),
    (u"a=b#c", [Binding(key=u"a", value=u"b#c", original=Original(string=u"a=b#c", line=1), error=False)]),
    (
        u'a=b #c',
        [Binding(key=u"a", value=u"b", original=Original(string=u"a=b #c", line=1), error=False)],
    ),
    (
        u'a=b\t#c',
        [Binding(key=u"a", value=u"b", original=Original(string=u"a=b\t#c", line=1), error=False)],
    ),
    (
        u"a=b c",
        [Binding(key=u"a", value=u"b c", original=Original(string=u"a=b c", line=1), error=False)],
    ),
    (
        u"a=b\tc",
        [Binding(key=u"a", value=u"b\tc", original=Original(string=u"a=b\tc", line=1), error=False)],
    ),
    (
        u"a=b  c",
        [Binding(key=u"a", value=u"b  c", original=Original(string=u"a=b  c", line=1), error=False)],
    ),
    (
        u"a=b\u00a0 c",
        [Binding(key=u"a", value=u"b\u00a0 c", original=Original(string=u"a=b\u00a0 c", line=1), error=False)],
    ),
    (
        u"a=b c ",
        [Binding(key=u"a", value=u"b c", original=Original(string=u"a=b c ", line=1), error=False)],
    ),
    (
        u"a='b c '",
        [Binding(key=u"a", value=u"b c ", original=Original(string=u"a='b c '", line=1), error=False)],
    ),
    (
        u'a="b c "',
        [Binding(key=u"a", value=u"b c ", original=Original(string=u'a="b c "', line=1), error=False)],
    ),
    (
        u"export export_a=1",
        [
            Binding(key=u"export_a", value=u"1", original=Original(string=u"export export_a=1", line=1), error=False)
        ],
    ),
    (
        u"export port=8000",
        [Binding(key=u"port", value=u"8000", original=Original(string=u"export port=8000", line=1), error=False)],
    ),
    (u'a="b\nc"', [Binding(key=u"a", value=u"b\nc", original=Original(string=u'a="b\nc"', line=1), error=False)]),
    (u"a='b\nc'", [Binding(key=u"a", value=u"b\nc", original=Original(string=u"a='b\nc'", line=1), error=False)]),
    (u'a="b\nc"', [Binding(key=u"a", value=u"b\nc", original=Original(string=u'a="b\nc"', line=1), error=False)]),
    (u'a="b\\nc"', [Binding(key=u"a", value=u'b\nc', original=Original(string=u'a="b\\nc"', line=1), error=False)]),
    (u"a='b\\nc'", [Binding(key=u"a", value=u'b\\nc', original=Original(string=u"a='b\\nc'", line=1), error=False)]),
    (u'a="b\\"c"', [Binding(key=u"a", value=u'b"c', original=Original(string=u'a="b\\"c"', line=1), error=False)]),
    (u"a='b\\'c'", [Binding(key=u"a", value=u"b'c", original=Original(string=u"a='b\\'c'", line=1), error=False)]),
    (u"a=à", [Binding(key=u"a", value=u"à", original=Original(string=u"a=à", line=1), error=False)]),
    (u'a="à"', [Binding(key=u"a", value=u"à", original=Original(string=u'a="à"', line=1), error=False)]),
    (
        u'no_value_var',
        [Binding(key=u'no_value_var', value=None, original=Original(string=u"no_value_var", line=1), error=False)],
    ),
    (u'a: b', [Binding(key=None, value=None, original=Original(string=u"a: b", line=1), error=True)]),
    (
        u"a=b\nc=d",
        [
            Binding(key=u"a", value=u"b", original=Original(string=u"a=b\n", line=1), error=False),
            Binding(key=u"c", value=u"d", original=Original(string=u"c=d", line=2), error=False),
        ],
    ),
    (
        u"a=b\rc=d",
        [
            Binding(key=u"a", value=u"b", original=Original(string=u"a=b\r", line=1), error=False),
            Binding(key=u"c", value=u"d", original=Original(string=u"c=d", line=2), error=False),
        ],
    ),
    (
        u"a=b\r\nc=d",
        [
            Binding(key=u"a", value=u"b", original=Original(string=u"a=b\r\n", line=1), error=False),
            Binding(key=u"c", value=u"d", original=Original(string=u"c=d", line=2), error=False),
        ],
    ),
    (
        u'a=\nb=c',
        [
            Binding(key=u"a", value=u'', original=Original(string=u'a=\n', line=1), error=False),
            Binding(key=u"b", value=u'c', original=Original(string=u"b=c", line=2), error=False),
        ]
    ),
    (
        u"\n\n",
        [
            Binding(key=None, value=None, original=Original(string=u"\n\n", line=1), error=False),
        ]
    ),
    (
        u"a=b\n\n",
        [
            Binding(key=u"a", value=u"b", original=Original(string=u"a=b\n", line=1), error=False),
            Binding(key=None, value=None, original=Original(string=u"\n", line=2), error=False),
        ]
    ),
    (
        u'a=b\n\nc=d',
        [
            Binding(key=u"a", value=u"b", original=Original(string=u"a=b\n", line=1), error=False),
            Binding(key=u"c", value=u"d", original=Original(string=u"\nc=d", line=2), error=False),
        ]
    ),
    (
        u'a="\nb=c',
        [
            Binding(key=None, value=None, original=Original(string=u'a="\n', line=1), error=True),
            Binding(key=u"b", value=u"c", original=Original(string=u"b=c", line=2), error=False),
        ]
    ),
    (
        u'# comment\na="b\nc"\nd=e\n',
        [
            Binding(key=None, value=None, original=Original(string=u"# comment\n", line=1), error=False),
            Binding(key=u"a", value=u"b\nc", original=Original(string=u'a="b\nc"\n', line=2), error=False),
            Binding(key=u"d", value=u"e", original=Original(string=u"d=e\n", line=4), error=False),
        ],
    ),
    (
        u'a=b\n# comment 1',
        [
            Binding(key="a", value="b", original=Original(string=u"a=b\n", line=1), error=False),
            Binding(key=None, value=None, original=Original(string=u"# comment 1", line=2), error=False),
        ],
    ),
    (
        u'# comment 1\n# comment 2',
        [
            Binding(key=None, value=None, original=Original(string=u"# comment 1\n", line=1), error=False),
            Binding(key=None, value=None, original=Original(string=u"# comment 2", line=2), error=False),
        ],
    ),
    (
        u'uglyKey[%$=\"S3cr3t_P4ssw#rD\" #\na=b',
        [
            Binding(key=u'uglyKey[%$',
                    value=u'S3cr3t_P4ssw#rD',
                    original=Original(string=u"uglyKey[%$=\"S3cr3t_P4ssw#rD\" #\n", line=1), error=False),
            Binding(key=u"a", value=u"b", original=Original(string=u'a=b', line=2), error=False),
        ],
    ),
])
def test_parse_stream(test_input, expected):
    result = parse_stream(io.StringIO(test_input))

    assert list(result) == expected
