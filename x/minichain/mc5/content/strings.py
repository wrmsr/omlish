import abc

from omlish import lang
from omlish.formats import json
from ommlds import minichain as mc


##


class ContentStringifier(lang.Abstract):
    @abc.abstractmethod
    def stringify_content(self, content: mc.Content) -> str | None:
        raise NotImplementedError


class ContentStringifierImpl(ContentStringifier):
    def stringify_content(self, content: mc.Content) -> str | None:
        if isinstance(content, str):
            return content

        elif isinstance(content, mc.JsonContent):
            return json.dumps_pretty(content.v)

        else:
            raise TypeError(content)
