"""
See:
 - https://github.com/simonw/llm
 - https://github.com/TheR1D/shell_gpt
 - https://github.com/paul-gauthier/aider
"""
import argparse
import dataclasses as dc
import datetime
import os.path
import sys
import typing as ta

from omlish import check
from omlish import lang
from omlish import logs
from omlish.diag import pycharm
from omlish.formats import json

from ..backends.anthropic import AnthropicChatModel
from ..backends.google import GoogleChatModel
from ..backends.llamacpp import LlamacppPromptModel
from ..backends.mistral import MistralChatModel
from ..backends.openai import OpenaiChatModel
from ..backends.openai import OpenaiEmbeddingModel
from ..backends.openai import OpenaiPromptModel
from ..backends.sentencetransformers import SentencetransformersEmbeddingModel
from ..backends.transformers import TransformersPromptModel
from ..chat import Chat
from ..chat import ChatModel
from ..chat import ChatRequest
from ..chat import UserMessage
from ..content import Content
from ..content import Image
from ..prompts import PromptModel
from ..prompts import PromptRequest
from ..vectors import EmbeddingModel
from ..vectors import EmbeddingRequest
from .state import load_state
from .state import save_state


if ta.TYPE_CHECKING:
    import PIL.Image as pimg  # noqa
else:
    pimg = lang.proxy_import('PIL.Image')


##


DEFAULT_BACKEND = 'openai'


##


@dc.dataclass(frozen=True)
class ChatState:
    name: str | None = None

    created_at: datetime.datetime = dc.field(default_factory=lang.utcnow)
    updated_at: datetime.datetime = dc.field(default_factory=lang.utcnow)

    chat: Chat = ()


CHAT_MODEL_BACKENDS: ta.Mapping[str, type[ChatModel]] = {
    'anthropic': AnthropicChatModel,
    'google': GoogleChatModel,
    'mistral': MistralChatModel,
    'openai': OpenaiChatModel,
}


def _run_chat(
        content: Content,
        *,
        new: bool = False,
        backend: str | None = None,
) -> None:
    prompt = check.isinstance(content, str)

    state_dir = os.path.expanduser('~/.omlish-llm')
    if not os.path.exists(state_dir):
        os.mkdir(state_dir)
        os.chmod(state_dir, 0o770)  # noqa

    chat_file = os.path.join(state_dir, 'chat.json')
    if new:
        state = ChatState()
    else:
        state = load_state(chat_file, ChatState)  # type: ignore
        if state is None:
            state = ChatState()  # type: ignore

    state = dc.replace(
        state,
        chat=[
            *state.chat,
            UserMessage(prompt),
        ],
    )

    mdl = CHAT_MODEL_BACKENDS[backend or DEFAULT_BACKEND]()
    response = mdl.invoke(ChatRequest.new(state.chat))
    print(check.isinstance(response.v[0].m.s, str).strip())

    chat = dc.replace(
        state,
        chat=[
            *state.chat,
            response.v[0].m,
        ],
    )

    chat = dc.replace(
        chat,
        updated_at=lang.utcnow(),
    )

    save_state(chat_file, chat, ChatState)


##


PROMPT_MODEL_BACKENDS: ta.Mapping[str, type[PromptModel]] = {
    'llamacpp': LlamacppPromptModel,
    'openai': OpenaiPromptModel,
    'transformers': TransformersPromptModel,
}


def _run_prompt(
        content: Content,
        *,
        backend: str | None = None,
) -> None:
    prompt = check.isinstance(content, str)
    mdl = PROMPT_MODEL_BACKENDS[backend or DEFAULT_BACKEND]()
    response = mdl.invoke(PromptRequest.new(prompt))
    print(response.v.strip())


##


EMBEDDING_MODEL_BACKENDS: ta.Mapping[str, type[EmbeddingModel]] = {
    'openai': OpenaiEmbeddingModel,
    'sentencetransformers': SentencetransformersEmbeddingModel,
}


def _run_embed(
        content: Content,
        *,
        backend: str | None = None,
) -> None:
    mdl = EMBEDDING_MODEL_BACKENDS[backend or DEFAULT_BACKEND]()
    response = mdl.invoke(EmbeddingRequest.new(content))
    print(json.dumps_compact(response.v))


##

def _main() -> None:
    logs.configure_standard_logging('INFO')

    #

    parser = argparse.ArgumentParser()
    parser.add_argument('prompt', nargs='+')

    parser.add_argument('-b', '--backend', default='openai')

    parser.add_argument('-c', '--chat', action='store_true')
    parser.add_argument('-n', '--new', action='store_true')
    parser.add_argument('-i', '--interactive', action='store_true')

    parser.add_argument('-e', '--embed', action='store_true')
    parser.add_argument('-j', '--image', action='store_true')

    args = parser.parse_args()

    #

    content: Content

    if args.image:
        content = Image(pimg.open(check.non_empty_str(check.single(args.prompt))))

    else:
        prompt = check.single(args.prompt)

        if not sys.stdin.isatty() and not pycharm.is_pycharm_hosted():
            stdin_data = sys.stdin.read()
            prompt = '\n'.join([prompt, stdin_data])

        content = prompt

    #

    with open(os.path.join(os.path.expanduser('~/.omlish-llm/.env'))) as f:
        for l in f:
            if l := l.strip():
                k, _, v = l.partition('=')
                os.environ[k] = v

    #

    if args.chat:
        _run_chat(
            content,
            backend=args.backend,
            new=bool(args.new),
        )

    elif args.embed:
        _run_embed(
            content,
            backend=args.backend,
        )

    else:
        _run_prompt(
            content,
            backend=args.backend,
        )


if __name__ == '__main__':
    _main()
