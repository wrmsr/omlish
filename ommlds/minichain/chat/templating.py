"""
TODO:
 - Chat unpacking convenience
"""
import abc
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish.text import templating as tpl

from ..content.transforms.strings import transform_content_strings
from ..envs import Env
from ..envs import EnvKey
from .messages import Chat
from .messages import Message


MessageT = ta.TypeVar('MessageT', bound=Message)

ChatTemplatePart: ta.TypeAlias = ta.Union[
    Message,
    'MessageTemplate',
    'MessagePlaceholder',
]

ChatTemplate: ta.TypeAlias = ta.Sequence[ChatTemplatePart]


##


class MessageTemplate(dc.Box[MessageT]):
    pass


@dc.dataclass(frozen=True)
class MessagePlaceholder:
    key: EnvKey


##


class ChatTemplater:
    def __init__(
            self,
            chat_template: ChatTemplate,
            *,
            template_factory: ta.Callable[[str], tpl.Templater] = tpl.JinjaTemplater.from_string,
    ) -> None:
        super().__init__()

        self._chat_template = chat_template
        self._template_factory = template_factory

        self._steps: list[ChatTemplater._Step] = [self._make_step(p) for p in chat_template]

    #

    class _Step(lang.Abstract):
        @abc.abstractmethod
        def render(self, env: Env) -> Chat:
            raise NotImplementedError

    @dc.dataclass(frozen=True)
    class _MessageStep(_Step):
        m: Message

        def render(self, env: Env) -> Chat:
            return [self.m]

    @dc.dataclass(frozen=True)
    class _TemplateStep(_Step):
        m: Message
        d: dict[str, tpl.Templater]

        def render(self, env: Env) -> Chat:
            def render_content_str(s: str) -> str:
                t = self.d[s]
                return t.render(tpl.Templater.Context(env))

            return [transform_content_strings(render_content_str, self.m)]

    @dc.dataclass(frozen=True)
    class _PlaceholderStep(_Step):
        p: MessagePlaceholder

        def render(self, env: Env) -> Chat:
            r = env[self.p.key]

            if isinstance(r, Message):
                return [r]

            elif isinstance(r, ta.Iterable):
                return [check.isinstance(e, Message) for e in r]

            else:
                raise TypeError(r)

    def _make_step(self, p: ChatTemplatePart) -> _Step:
        if isinstance(p, Message):
            return self._MessageStep(p)

        elif isinstance(p, MessageTemplate):
            content_strs: set[str] = set()

            def visit_content_str(s: str) -> str:
                content_strs.add(s)
                return s

            transform_content_strings(visit_content_str, p.v)

            d: dict[str, tpl.Templater] = {
                s: self._template_factory(s)
                for s in content_strs
            }

            return self._TemplateStep(p.v, d)

        elif isinstance(p, MessagePlaceholder):
            return self._PlaceholderStep(p)

        else:
            raise TypeError(p)

    #

    def render(self, env: Env) -> Chat:
        return list(lang.flatten(
            step.render(env)
            for step in self._steps
        ))
