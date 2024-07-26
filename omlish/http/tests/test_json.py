# Copyright 2010 Pallets
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1.  Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#     disclaimer.
#
# 2.  Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#     following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3.  Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#     products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import datetime
import uuid

import markupsafe
import pytest

from ..json import JsonTag
from ..json import JsonTagger


@pytest.mark.parametrize(
    'data',
    [
        {' t': (1, 2, 3)},
        {' t__': b'a'},
        {' di': ' di'},
        {'x': (1, 2, 3), 'y': 4},
        (1, 2, 3),
        [(1, 2, 3)],
        b'\xff',
        markupsafe.Markup('<html>'),
        uuid.uuid4(),
        datetime.datetime.now(tz=datetime.UTC).replace(microsecond=0),
    ],
)
def test_dump_load_unchanged(data):
    s = JsonTagger()
    print()
    print(data)
    print(s.dumps(data))
    print()
    assert s.loads(s.dumps(data)) == data


def test_duplicate_tag():
    class TagDict2(JsonTag):
        key = ' d'

    s = JsonTagger()
    pytest.raises(KeyError, s.register, TagDict2)
    s.register(TagDict2, force=True, index=0)
    assert isinstance(s.tags[' d'], TagDict2)
    assert isinstance(s.order[0], TagDict2)


def test_custom_tag():
    class Foo:  # noqa: B903, for Python2 compatibility
        def __init__(self, data):
            self.data = data

    class TagFoo(JsonTag):
        __slots__ = ()
        key = ' f'

        def check(self, value):
            return isinstance(value, Foo)

        def to_json(self, value):
            return self.tagger.tag(value.data)

        def to_python(self, value):
            return Foo(value)

    s = JsonTagger()
    s.register(TagFoo)
    assert s.loads(s.dumps(Foo('bar'))).data == 'bar'


def test_tag_interface():
    t = JsonTag(None)  # type: ignore
    pytest.raises(NotImplementedError, t.check, None)
    pytest.raises(NotImplementedError, t.to_json, None)
    pytest.raises(NotImplementedError, t.to_python, None)


def test_tag_order():
    class Tag1(JsonTag):
        key = ' 1'

    class Tag2(JsonTag):
        key = ' 2'

    s = JsonTagger()

    s.register(Tag1, index=-1)
    assert isinstance(s.order[-2], Tag1)

    s.register(Tag2, index=None)
    assert isinstance(s.order[-1], Tag2)
