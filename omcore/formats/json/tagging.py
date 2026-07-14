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
import base64
import typing as ta

from ... import lang
from .backends import default_backend


##


class JsonTag(lang.Abstract):
    key: str = ''

    def __init__(self, tagger: JsonTagger) -> None:
        super().__init__()

        self.tagger = tagger

    def check(self, value: ta.Any) -> bool:
        raise NotImplementedError

    def to_json(self, value: ta.Any) -> ta.Any:
        raise NotImplementedError

    def to_python(self, value: ta.Any) -> ta.Any:
        raise NotImplementedError

    def tag(self, value: ta.Any) -> dict[str, ta.Any]:
        return {self.key: self.to_json(value)}


class DictJsonTag(JsonTag):
    key = ' di'

    def check(self, value: ta.Any) -> bool:
        return (
            isinstance(value, dict) and
            len(value) == 1 and
            next(iter(value)) in self.tagger.tags
        )

    def to_json(self, value: ta.Any) -> ta.Any:
        key = next(iter(value))
        return {f'{key}__': self.tagger.tag(value[key])}

    def to_python(self, value: ta.Any) -> ta.Any:
        key = next(iter(value))
        return {key[:-2]: value[key]}


class PassDictJsonTag(JsonTag):
    def check(self, value: ta.Any) -> bool:
        return isinstance(value, dict)

    def to_json(self, value: ta.Any) -> ta.Any:
        return {k: self.tagger.tag(v) for k, v in value.items()}

    tag = to_json


class TupleJsonTag(JsonTag):
    key = ' t'

    def check(self, value: ta.Any) -> bool:
        return isinstance(value, tuple)

    def to_json(self, value: ta.Any) -> ta.Any:
        return [self.tagger.tag(item) for item in value]

    def to_python(self, value: ta.Any) -> ta.Any:
        return tuple(value)


class PassListJsonTag(JsonTag):
    def check(self, value: ta.Any) -> bool:
        return isinstance(value, list)

    def to_json(self, value: ta.Any) -> ta.Any:
        return [self.tagger.tag(item) for item in value]

    tag = to_json


class BytesJsonTag(JsonTag):
    key = ' b'

    def check(self, value: ta.Any) -> bool:
        return isinstance(value, bytes)

    def to_json(self, value: ta.Any) -> ta.Any:
        return base64.b64encode(value).decode('ascii')

    def to_python(self, value: ta.Any) -> ta.Any:
        return base64.b64decode(value)


class JsonTagger:
    DEFAULT_TAGS: ta.ClassVar[ta.Sequence[type[JsonTag]]] = [
        DictJsonTag,
        PassDictJsonTag,
        TupleJsonTag,
        PassListJsonTag,
        BytesJsonTag,
    ]

    def __init__(self) -> None:
        super().__init__()

        self.tags: dict[str, JsonTag] = {}
        self.order: list[JsonTag] = []

        for cls in self.DEFAULT_TAGS:
            self.register(cls)

    def register(
            self,
            tag_class: type[JsonTag],
            force: bool = False,
            index: int | None = None,
    ) -> None:
        tag = tag_class(self)
        key = tag.key

        if key:
            if not force and key in self.tags:
                raise KeyError(f"Tag '{key}' is already registered.")

            self.tags[key] = tag

        if index is None:
            self.order.append(tag)
        else:
            self.order.insert(index, tag)

    def tag(self, value: ta.Any) -> ta.Any:
        for tag in self.order:
            if tag.check(value):
                return tag.tag(value)

        return value

    def untag(self, value: dict[str, ta.Any]) -> ta.Any:
        if len(value) != 1:
            return value

        key = next(iter(value))

        if key not in self.tags:
            return value

        return self.tags[key].to_python(value[key])

    def untag_scan(self, value: ta.Any) -> ta.Any:
        if isinstance(value, dict):
            value = {k: self.untag_scan(v) for k, v in value.items()}
            value = self.untag(value)

        elif isinstance(value, list):
            value = [self.untag_scan(item) for item in value]

        return value

    def dumps(self, value: ta.Any) -> str:
        return default_backend().dumps_compact(self.tag(value))

    def loads(self, value: str) -> ta.Any:
        return self.untag_scan(default_backend().loads(value))


JSON_TAGGER = JsonTagger()
