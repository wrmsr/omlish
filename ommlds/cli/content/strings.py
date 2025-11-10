import abc
import typing as ta

from omlish import lang
from omlish.formats import json

from ... import minichain as mc


##


class ContentStringifier(lang.Abstract):
    @abc.abstractmethod
    def stringify_content(self, content: 'mc.Content') -> str | None:
        raise NotImplementedError


class ContentStringifierImpl(ContentStringifier):
    def stringify_content(self, content: 'mc.Content') -> str | None:
        if isinstance(content, str):
            return content

        elif isinstance(content, mc.JsonContent):
            return json.dumps_pretty(content.v)

        else:
            raise TypeError(content)


class HasContentStringifier(lang.Abstract):
    def __init__(
            self,
            *args: ta.Any,
            content_stringifier: ContentStringifier | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        if content_stringifier is None:
            content_stringifier = ContentStringifierImpl()
        self._content_stringifier = content_stringifier
