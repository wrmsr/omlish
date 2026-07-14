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
import dataclasses as dc
import datetime
import decimal
import json as _json
import typing as ta
import uuid

from .. import lang
from ..formats.json.tagging import JsonTag
from ..formats.json.tagging import JsonTagger as BaseJsonTagger
from .dates import http_date
from .dates import parse_date


if ta.TYPE_CHECKING:
    import markupsafe
else:
    markupsafe = lang.proxy_import('markupsafe')


##


def _default(o: ta.Any) -> ta.Any:
    if isinstance(o, datetime.date):
        return http_date(o)

    if isinstance(o, (decimal.Decimal, uuid.UUID)):
        return str(o)

    if dc.is_dataclass(o):
        return dc.asdict(o)  # type: ignore

    if hasattr(o, '__html__'):
        return str(o.__html__())

    raise TypeError(f'Object of type {type(o).__name__} is not Json serializable')


def json_dumps(obj: ta.Any, **kwargs: ta.Any) -> str:
    kwargs.setdefault('default', _default)
    return _json.dumps(obj, **kwargs)


def json_loads(s: str | bytes, **kwargs: ta.Any) -> ta.Any:
    return _json.loads(s, **kwargs)


##


class MarkupJsonTag(JsonTag):
    key = ' m'

    def check(self, value: ta.Any) -> bool:
        return callable(getattr(value, '__html__', None))

    def to_json(self, value: ta.Any) -> ta.Any:
        return str(value.__html__())

    def to_python(self, value: ta.Any) -> ta.Any:
        return markupsafe.Markup(value)


class UuidJsonTag(JsonTag):
    key = ' u'

    def check(self, value: ta.Any) -> bool:
        return isinstance(value, uuid.UUID)

    def to_json(self, value: ta.Any) -> ta.Any:
        return value.hex

    def to_python(self, value: ta.Any) -> ta.Any:
        return uuid.UUID(value)


class DatetimeJsonTag(JsonTag):
    key = ' dt'

    def check(self, value: ta.Any) -> bool:
        return isinstance(value, datetime.datetime)

    def to_json(self, value: ta.Any) -> ta.Any:
        return http_date(value)

    def to_python(self, value: ta.Any) -> ta.Any:
        return parse_date(value)


class JsonTagger(BaseJsonTagger):
    DEFAULT_TAGS: ta.ClassVar[ta.Sequence[type[JsonTag]]] = [
        *BaseJsonTagger.DEFAULT_TAGS,
        *([MarkupJsonTag] if lang.can_import('markupsafe') else []),
        UuidJsonTag,
        DatetimeJsonTag,
    ]

    def dumps(self, value: ta.Any) -> str:
        return json_dumps(self.tag(value), separators=(',', ':'))

    def loads(self, value: str) -> ta.Any:
        return self.untag_scan(json_loads(value))


JSON_TAGGER = JsonTagger()
